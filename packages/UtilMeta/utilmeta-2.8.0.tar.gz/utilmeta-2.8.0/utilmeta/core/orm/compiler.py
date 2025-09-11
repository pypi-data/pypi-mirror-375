from .parser import SchemaClassParser
from .fields.field import ParserQueryField
from .context import QueryContext
from typing import List, Any, Dict, Tuple, Type, Union, TYPE_CHECKING
from utilmeta.utils import awaitable
from utilmeta.conf import Preference
from utype import unprovided, Options, Schema

if TYPE_CHECKING:
    from .backends.base import ModelAdaptor


class TransactionWrapper:
    def __init__(
        self,
        model: "ModelAdaptor",
        transaction: Union[str, bool] = False,
        errors_map: dict = None,
    ):
        # self.enabled = bool(transaction)
        db_alias = None
        if isinstance(transaction, str):
            db_alias = transaction
        elif transaction:
            # get the default db
            db_alias = model.default_db_alias
        # if not db_alias:
        #     self.enabled = False
        self.db_alias = db_alias

        from .plugins.atomic import AtomicPlugin

        self.atomic = AtomicPlugin(db_alias) if db_alias else None
        self.errors_map = errors_map or {}

    def handle_error(self, e: Exception):
        for errors, target in self.errors_map.items():
            if isinstance(e, errors):
                raise target(e) from e
        raise e.__class__(str(e)) from e

    def __enter__(self):
        if self.atomic:
            return self.atomic.__enter__()
        return self

    async def __aenter__(self):
        if self.atomic:
            return await self.atomic.__aenter__()
        return self

    # def __await__(self):
    #     if self.atomic:
    #         return self.atomic.__await__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.atomic:
            try:
                return self.atomic.__exit__(exc_type, exc_val, exc_tb)
            except Exception as e:
                # try:
                #     if not exc_type:
                #         return self.atomic.__exit__(e.__class__, e, e.__traceback__)
                # finally:
                self.handle_error(e)

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.atomic:
            try:
                return await self.atomic.__aexit__(exc_type, exc_val, exc_tb)
            except Exception as e:
                # try:
                #     if not exc_type:
                #         # SQLite error will be raised on COMMIT statement inside transaction
                #         # so when the COMMIT failed (in the __exit__ block)
                #         # we should rollback with exceptions passed in
                #         return await self.atomic.__aexit__(e.__class__, e, e.__traceback__)
                # finally:
                self.handle_error(e)

    # def rollback(self):
    #     if self.atomic:
    #         return self.atomic.rollback()
    #
    # def commit(self):
    #     if self.atomic:
    #         return self.atomic.commit()


class BaseQueryCompiler:
    def __init__(
        self, parser: SchemaClassParser, queryset, context: QueryContext = None
    ):
        parser.resolve_forward_refs()
        # resolve unresolved forward refs when query compiler is built (related schema might be resolved)
        self.parser = parser
        self.model = parser.model
        if not self.model:
            raise NotImplementedError(
                f"{self.__class__.__name__}: model for {parser.obj} is unset"
            )

        from .backends.base import ModelQueryAdaptor

        query_adaptor = None
        using = None
        if isinstance(queryset, ModelQueryAdaptor):
            query_adaptor = queryset
            using = query_adaptor.using
            queryset = queryset.queryset

        self.queryset = queryset
        self.query_adaptor = query_adaptor
        self.context = context or QueryContext()
        if using and not self.context.using:
            self.context.using = using

        self.recursion_map: Dict[Any, Dict[Any, dict]] = (
            self.context.recursion_map or {}
        )
        # purposes:
        # 1. avoid infinite recursion
        #    for recursion duplicate objects, only give a schema with values field (not relation fields)
        # 2. reduce redundant schema queries

        self.pk_map = {}
        # self.recursive_pk_list = []
        self.recursively = False
        self.pk_list = []
        # self.recursively = False
        self.values: List[dict] = []
        self.pref = Preference.get()
        self.gather_async_fields = self.context.gather_async_fields
        if self.gather_async_fields is None:
            self.gather_async_fields = self.pref.orm_default_gather_async_fields
        if (
            self.pref.orm_schema_query_max_depth
            and self.context.depth > self.pref.orm_schema_query_max_depth
        ):
            raise RecursionError(
                f"{self.parser.obj}: schema query depth exceed orm_schema_query_max_depth: "
                f"{self.pref.orm_schema_query_max_depth}, there might be some kind of"
                f" unresolvable infinite recursion"
            )

    @property
    def orm_model(self):
        if self.model:
            return self.model.model
        return None

    @property
    def ident(self):
        return self.parser.obj

    @property
    def using(self):
        return self.context.using

    def get_integrity_error(self, e: Exception) -> Exception:
        if self.context.integrity_error_cls:
            return self.context.integrity_error_cls(e)
        return e

    def get_related_context(
        self,
        field: ParserQueryField,
        force_expressions: dict = None,
        force_raise_error: bool = False,
    ):
        includes = excludes = None
        if self.context.includes:
            inter = set(self.context.includes).intersection(field.all_aliases)
            includes = self.context.includes.get(inter.pop()) if inter else None
        if self.context.excludes:
            inter = set(self.context.excludes).intersection(field.all_aliases)
            excludes = self.context.excludes.get(inter.pop()) if inter else None
        routes = [(field.name, field.related_schema)]
        relation_routes = (self.context.relation_routes or []) + routes
        return QueryContext(
            self.context.request,
            using=self.context.using,
            # single=field.related_single,
            single=False,  # not make it single, related context is always about multiple
            includes=includes,
            excludes=excludes,
            recursion_map=dict(self.recursion_map),
            # avoid sharing the same recursion map to different relation fields
            force_expressions=force_expressions,
            force_raise_error=force_raise_error or self.context.force_raise_error,
            integrity_error_cls=self.context.integrity_error_cls,
            relation_routes=relation_routes,
            depth=self.context.depth + 1,
        )

    @property
    def serialize_options(self) -> Options:
        options = getattr(
            self.parser.obj,
            "__serialize_options__",
            Options(
                mode="r",
                addition=True,
                ignore_required=True,
                ignore_constraints=True
            ),
        )  # original options
        if self.context.includes:
            options = options & Options(defer_default=True)
            # prevent defaults in includes
        elif self.context.excludes:
            options = options & Options(
                defer_default=list(self.context.excludes)
                # supported in utype >= 0.6.7
            )
        return options

    def get_recursion_objects(self, schema_cls: Type[Schema], *pks):
        mp = {}
        if not pks:
            return mp
        if schema_cls not in self.recursion_map:
            return mp
        schema_mp = self.recursion_map[schema_cls]
        for pk in pks:
            value = schema_mp.get(pk)
            if not value:
                continue
            if not isinstance(value, schema_cls) and isinstance(value, dict):
                try:
                    value = schema_cls.__from__(
                        {
                            key: val
                            for key, val in value.items()
                            if not str(key).startswith("__")
                        },
                        self.serialize_options,
                    )
                except Exception as e:
                    print(
                        f"serialize recursion value: {schema_cls}(pk={repr(pk)}) with error",
                        e,
                    )
                    continue
            mp[pk] = value
        return mp

    def _resolve_recursion(self):
        recursion_map = self.recursion_map
        # recursion map is isolated among fields
        if recursion_map and self.ident in recursion_map:
            recursive_pks = recursion_map.get(self.ident)
            recursive_pks.update(self.pk_map)
            # across = recursive_pks.intersection(self.pk_list)
            # if across:
            #     warnings.warn(f'{self}: execute query detect recursive ({across}), these objects '
            #                   f'will not recursively included in the result')
            #     self.recursive_pk_list = [pk for pk in self.pk_list if pk not in across]
            #     if not self.pk_list:
            #         # directly return
            #         return []
            # update the reset pk list
            # recursive_pks.update(self.pk_list)
        elif self.recursively:
            recursion_map = recursion_map or {}
            recursion_map[self.ident] = dict(self.pk_map)
        self.recursion_map = recursion_map

    def base_queryset(self):
        return self.model.get_queryset()

    def process_query_field(self, field: ParserQueryField):
        if field.related_schema:
            self.recursively = True

    def process_fields(self):
        for name, field in self.parser.fields.items():
            if not isinstance(field, ParserQueryField):
                continue
            if not field.readable:
                continue
            if not self.context.in_scope(
                field.all_aliases,
                dependents=getattr(field, 'dependents', getattr(field, 'dependants', None)),
                # for utype > 0.7, this will be dependents=field.dependents
                default_included=field.default_included
            ):
                continue
            self.process_query_field(field)

    def get_values(self) -> List[dict]:
        raise NotImplementedError

    @awaitable(get_values)
    async def get_values(self) -> List[dict]:
        raise NotImplementedError

    def process_data(
        self, data: dict, with_relations: bool = None
    ) -> Tuple[dict, dict, dict]:
        if not isinstance(data, dict):
            return {}, {}, {}
        if not isinstance(data, self.parser.obj):
            data = self.parser(data)
        if with_relations is None:
            with_relations = self.pref.orm_default_save_with_relations

        result = {}
        relation_keys = {}
        relation_objs = {}

        for key, val in data.items():
            field = self.parser.get_field(key)
            if not isinstance(field, ParserQueryField):
                continue
            if not field.writable and not field.primary_key:
                # RELATIONS FIELD HERE
                if with_relations:
                    if field.relation_update_enabled:
                        if val is None and field.many_included:
                            # 1. for many related field, providing None is considered invalid
                            # providing an empty list [] will empty all the relations
                            # 2. for single relation that supported update
                            # providing None (in update mode in output) means to set None the reverse fk
                            continue

                        if field.related_schema:
                            relation_objs[key] = (field, val)
                        else:
                            name = field.model_field.name
                            if not name:
                                continue
                            relation_keys[name] = (field, val)
                continue
            name = field.model_field.column_name
            # fk will be fk_id in this case
            if not isinstance(name, str):
                continue
            value = self.process_value(field, val)
            if not unprovided(value):
                result[name] = value

        return result, relation_keys, relation_objs

    def process_value(self, field: ParserQueryField, value):
        return value

    def commit_data(self, data):
        raise NotImplementedError

    @awaitable(commit_data)
    async def commit_data(self, data):
        raise NotImplementedError

    def save_data(
        self,
        data,
        must_create: bool = False,
        must_update: bool = False,
        ignore_bulk_errors: bool = False,
        ignore_relation_errors: bool = False,
        with_relations: bool = None,
        transaction: bool = False,
    ):
        raise NotImplementedError

    @awaitable(save_data)
    async def save_data(
        self,
        data,
        must_create: bool = False,
        must_update: bool = False,
        ignore_bulk_errors: bool = False,
        ignore_relation_errors: bool = False,
        with_relations: bool = None,
        transaction: bool = False,
    ):
        raise NotImplementedError

    def get_integrity_errors(
        self, asynchronous: bool = False
    ) -> Tuple[Type[Exception], ...]:
        return ()
