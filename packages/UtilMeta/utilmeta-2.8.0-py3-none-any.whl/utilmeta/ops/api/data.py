from utilmeta.core import api, request, orm
from .utils import SupervisorObject, supervisor_var, WrappedResponse, opsRequire
from utilmeta.utils import reduce_value, SECRET, adapt_async, exceptions, awaitable, pop
from ..schema import TableSchema, QuerySchema, CreateDataSchema, UpdateDataSchema
from utilmeta.core.orm import ModelAdaptor
from utype.types import *
from .utils import config


_tables: Optional[list] = None


class DataAPI(api.API):
    supervisor: SupervisorObject = supervisor_var
    response = WrappedResponse

    model: str = request.QueryParam(required=True)
    # model ref
    using: str = request.QueryParam(default=None)

    def get_model(self):
        if "." not in self.model:
            return None
        # security check
        tables = self.get_tables()
        for table in tables:
            if table.get("ref") == self.model:
                if table.model:
                    return table.model
        raise exceptions.BadRequest(f"Invalid model: {self.model}")
        # deprecate the import usage as it maybe dangerous

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._adaptor = None
        # not trigger adaptor load until the first access
        self.model_class = None
        self.database = None
        self.check_using()

    def check_using(self):
        if self.using:
            from utilmeta.core.orm import DatabaseConnections
            try:
                self.database = DatabaseConnections.get(self.using)
            except exceptions.NotConfigured:
                raise exceptions.BadRequest(
                    f"Invalid database alias: {repr(self.using)}"
                )

    @property
    def adaptor(self) -> ModelAdaptor:
        if self._adaptor:
            return self._adaptor
        self.model_class = self.get_model()
        try:
            self._adaptor = ModelAdaptor.dispatch(self.model_class)
        except NotImplementedError:
            raise exceptions.BadRequest(f"Invalid model: {self.model}")
        return self._adaptor

    @property
    def queryset(self):
        return self.adaptor.query(self.using)

    def parse_result(self, data, max_length: Optional[int] = None):
        if isinstance(data, list):
            for d in data:
                self.parse_result(d, max_length=max_length)
            return data
        elif isinstance(data, dict):
            for k in list(data.keys()):
                if k == "pk":
                    continue
                field = self.adaptor.get_field(k)
                if config.is_secret(k) and not field.related_model:
                    if data[k] and not isinstance(data[k], bool):
                        # if value is empty string or None, keep it the same
                        data[k] = SECRET
                if isinstance(max_length, int):
                    data[k] = reduce_value(data[k], max_length=max_length)
            return data
        return reduce_value(data, max_length=max_length)

    @api.get("tables")
    @opsRequire("data.view")
    def get_tables(self) -> List[TableSchema]:
        global _tables
        if _tables is not None:
            return _tables
        from ..resources import ResourcesManager

        _tables = ResourcesManager().get_tables(with_model=True)
        return _tables

    # scope: data.view:[TABLE_IDENT]
    @api.post("query")
    @opsRequire("data.query")
    @adapt_async(close_conn=True)
    # close all connections
    def query_data(self, query: QuerySchema = request.Body):
        try:
            unsliced_qs = self.adaptor.get_queryset(query.query, using=self.using)
            count = unsliced_qs.count()
            qs = unsliced_qs.order_by(*query.orders)[
                (query.page - 1) * query.rows: query.page * query.rows
            ]
            # todo: adaptor for other ORM vendors
            fields = query.fields
            if not fields:
                fields = ["pk"] + [
                    f.column_name
                    for f in self.adaptor.get_fields(many=False, no_inherit=True)
                    if f.column_name
                ]
            values = self.adaptor.query(qs, using=self.using).values(*fields)
        except self.adaptor.field_errors as e:
            raise exceptions.BadRequest(str(e)) from e
        return self.response(
            self.parse_result(values, max_length=query.max_length), count=count
        )

    @api.post("create")
    @opsRequire("data.create")
    @adapt_async(close_conn=True)
    # close all connections
    def create_data(self, data: CreateDataSchema = request.Body):
        objs = []
        with orm.Atomic(self.using):
            for val in data.data:
                try:
                    objs.append(self.adaptor.query(using=self.using).create(val))
                except self.adaptor.integrity_errors as e:
                    raise exceptions.BadRequest(str(e)) from e
        if not data.return_fields:
            return
        qs = self.adaptor.get_queryset(objs, using=self.using)
        values = self.adaptor.query(qs, using=self.using).values(*data.return_fields)
        return self.parse_result(values, max_length=data.return_max_length)

    @api.post("update")
    @opsRequire("data.update")
    @adapt_async(close_conn=True)
    # close all connections
    def update_data(self, data: UpdateDataSchema = request.Body):
        rows = 0
        with orm.Atomic(self.using):
            for val in data.data:
                pk = pop(val, "pk") or pop(val, "id")
                if pk:
                    try:
                        r = self.adaptor.query(pk=pk, using=self.using).update(val)
                    except self.adaptor.integrity_errors as e:
                        raise exceptions.BadRequest(str(e)) from e
                    if r and isinstance(r, int):
                        rows += r
        return rows

    def delete_data(
        self,
        id: str = request.BodyParam
        # query: dict = request.BodyParam,
        # limit: Optional[int] = request.BodyParam(None)
    ) -> int:
        # qs = self.adaptor.get_queryset(**query)
        # if limit is not None:
        #     qs = qs.order_by('pk')[:limit]
        return self.adaptor.query(pk=id, using=self.using).delete()

    @api.post("delete")
    @opsRequire("data.delete")
    @awaitable(delete_data)
    async def delete_data(self, id: str = request.BodyParam) -> int:
        # apply for async CASCADE
        return await self.adaptor.query(pk=id, using=self.using).adelete()
