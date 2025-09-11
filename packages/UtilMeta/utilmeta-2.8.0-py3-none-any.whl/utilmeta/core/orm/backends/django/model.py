from utilmeta.utils import SEG, awaitable
from ..base import ModelFieldAdaptor, ModelAdaptor
from typing import Tuple, Optional, List, Callable, Type

from django.db import models
from django.db.models.base import ModelBase
from django.db.models.options import Options
from django.db.utils import IntegrityError
from django.core import exceptions as exc
from . import constant
from . import expressions as exp
import django
from .field import DjangoModelFieldAdaptor, many_to
from .query import DjangoModelQueryAdaptor
from .generator import DjangoQuerysetGenerator
from .compiler import DjangoQueryCompiler


class DjangoModelAdaptor(ModelAdaptor):
    # Model adaptor is the entry point to all the orm adaptors
    # (like server adaptor is the entry point for request/response adaptor)
    backend = django
    backend_name = 'django'
    field_adaptor_cls = DjangoModelFieldAdaptor
    query_adaptor_cls = DjangoModelQueryAdaptor
    generator_cls = DjangoQuerysetGenerator
    compiler_cls = DjangoQueryCompiler
    model_cls = models.Model
    queryset_cls = models.QuerySet
    model: Type[models.Model]

    @property
    def ident(self):
        meta = self.meta
        if not meta:
            return ""
        app_label = meta.app_label
        tag = ".".join((app_label, self.model.__name__))
        return tag.lower()

    @property
    def field_errors(self) -> Tuple[Type[Exception], ...]:
        return (exc.FieldError,)

    @property
    def integrity_errors(self) -> Tuple[Type[Exception], ...]:
        return (IntegrityError,)

    @classmethod
    def qualify(cls, obj):
        return isinstance(obj, ModelBase)

    @property
    def pk_field(self) -> field_adaptor_cls:
        return self.field_adaptor_cls(self.meta.pk)

    def get_pk(self, data: dict):
        pk = self.pk_field
        for name in [pk.name, pk.column_name, 'id', 'pk']:
            v = data.get(name)
            if v is not None:
                return v
        return None

    def init_instance(self, pk=None, **data):
        if pk:
            data.setdefault("pk", pk)
        obj = self.model(**data)
        if getattr(obj, "id", None) is None:
            setattr(obj, "id", obj.pk or pk)
        return obj

    def check_subquery(self, qs):
        if not isinstance(qs, self.queryset_cls):
            return False
        if len(qs.query.select) > 1:
            # django.core.exceptions.FieldError: Cannot resolve expression type, unknown output_field
            raise ValueError(f"Multiple fields selected in related queryset: {qs}")
        if qs.query.is_sliced:
            hi = qs.query.high_mark
            lo = qs.query.low_mark
            if hi is not None and lo is not None:
                if hi - lo == 1:
                    return True
        raise ValueError("subquery result must be limited to 1 result")

    def check_queryset(self, qs, check_model: bool = False) -> Optional[query_adaptor_cls]:
        if not isinstance(qs, self.queryset_cls):
            return None
        if check_model:
            model = qs.model
            if not issubclass(self.model, model):
                return None
        return self.query_adaptor_cls(qs, model=self)

    def get_model(self, qs: models.QuerySet):
        if not isinstance(qs, self.queryset_cls):
            raise TypeError(f"Invalid queryset: {qs}")
        return self.__class__(qs.model)

    @property
    def meta(self) -> Options:
        return getattr(self.model, "_meta")

    @property
    def abstract(self):
        """
        Do not corresponding to a concrete table
        """
        return self.meta.abstract

    @property
    def table_name(self):
        return self.meta.db_table

    @property
    def default_db_alias(self) -> str:
        return self.get_queryset().db or "default"

    def get_parents(self):
        return self.meta.parents

    def cross_models(self, field: str):
        if not isinstance(field, str):
            return False
        return "." in field or "__" in field

    def get_field(
        self,
        name: str,
        validator: Callable = None,
        silently: bool = False,
    ) -> Optional[field_adaptor_cls]:
        """
        Get name from a field references
        """
        if not name:
            if silently:
                return None
            raise ValueError(f"{self.model}: empty field")

        if not isinstance(name, str):
            # field ref / expression
            try:
                return self.field_adaptor_cls(name, model=self)
            except TypeError:
                if silently:
                    return None
                raise

        if name == "pk":
            return self.field_adaptor_cls(self.meta.pk, model=self)

        model = self.model
        query_name = name.replace(".", SEG)
        lookups = query_name.split(SEG)

        f: Optional[models.Field] = None
        field_transform = None
        query_lookup = None

        for i, lk in enumerate(lookups):
            if not model:
                # get lookup
                # get transform
                if f:
                    try:
                        trans = f.get_transform(lk)
                        if not trans:
                            raise exc.FieldDoesNotExist
                    except (exc.FieldError, exc.FieldDoesNotExist, AttributeError):
                        try:
                            lookup = f.get_lookup(lk)
                            if not lookup:
                                raise exc.FieldDoesNotExist
                        except (exc.FieldError, exc.FieldDoesNotExist, AttributeError):
                            pass
                        else:
                            query_lookup = lk
                            break
                    else:
                        field_transform = lk
                        break

                if silently:
                    return None
                raise exc.FieldDoesNotExist(
                    f"Field: {repr(query_name)} of {self.model} not found"
                )

            try:
                meta: Options = getattr(model, "_meta")
                f = meta.get_field(lk)
                if callable(validator):
                    validator(f)
                model = f.related_model
            except exc.FieldDoesNotExist as e:
                if silently:
                    return None
                msg = f"Field: {repr(query_name)} of {self.model} not found"
                if model != self.model:
                    msg += f": lookup {repr(lk)} of model {model} not exists"
                raise exc.FieldDoesNotExist(msg) from e

        try:
            return self.field_adaptor_cls(
                f,
                model=self,
                transform_name=field_transform,
                query_lookup=query_lookup,
                query_name=query_name
            )
        except (TypeError, ValueError, exc.FieldDoesNotExist):
            if silently:
                return None
            raise

    def get_backward(self, field: str) -> str:
        raise NotImplementedError

    def get_reverse_lookup(self, lookup: str) -> Tuple[str, Optional[str]]:
        reverse_fields = []
        lookups = lookup.replace(".", SEG).split(SEG)
        _model = self
        # relate1__relate2__common1__common2
        common_index = None
        common_field = ""
        for i, name in enumerate(lookups):
            field = _model.get_field(name)
            if field.remote_field:
                if not field.remote_field.is_pk:
                    reverse_fields.append(field.remote_field.name)
                _model = field.related_model
            else:
                common_index = i
                break
        if common_index is not None:
            common_field = SEG.join(lookups[common_index:])
        reverse_fields.reverse()
        return SEG.join(reverse_fields), common_field

    def get_last_many_relates(self, lookup: str):
        raise NotImplementedError

    def get_fields(self, many=False, no_inherit=False) -> List[ModelFieldAdaptor]:
        meta = self.meta
        if not meta:
            return []
        fields = []
        pk = meta.pk
        if pk:
            # abstract model meta.pk is None
            fields.append(DjangoModelFieldAdaptor(pk, model=self))
        for f in meta.get_fields() if many else meta.fields:
            try:
                field = self.field_adaptor_cls(f)
            except TypeError:
                # not qualified
                continue
            if field.is_pk:
                continue
            if f.remote_field:
                try:
                    remote_field = self.field_adaptor_cls(f.remote_field)
                except TypeError:
                    # not qualified
                    continue
                if remote_field.is_pk:
                    continue
            if no_inherit:
                if f.model != self.model:
                    # parent model
                    continue
            if many:
                try:
                    self.get_field(f.name)
                except exc.FieldDoesNotExist:
                    continue
            fields.append(DjangoModelFieldAdaptor(f, model=self))
        return fields

    def get_related_adaptor(self, field):
        return self.__class__(field.related_model) if field.related_model else None

    def gen_lookup_keys(
        self, field: str, keys, strict: bool = True, excludes: List[str] = None
    ) -> list:
        raise NotImplementedError

    def gen_lookup_filter(self, field, q, excludes: List[str] = None):
        raise NotImplementedError

    def include_many_relates(self, field: str):
        if not field:
            return False
        if isinstance(field, (exp.BaseExpression, exp.Combinable)):
            return self.include_many_relates(
                self.field_adaptor_cls.get_exp_field(field)
            )
        if not isinstance(field, str):
            return False
        lookups = field.replace(".", SEG).split(SEG)
        mod = self.model
        for lkp in lookups:
            try:
                f = mod._meta.get_field(lkp)
            except exc.FieldDoesNotExist:
                return False
            if many_to(f):
                return True
            mod = f.related_model
            if not mod:
                return False
        return False

    def resolve_output_field(self, expr):
        if isinstance(expr, exp.CombinedExpression):
            try:
                return expr.output_field
            except (exc.FieldError, AttributeError, TypeError, ValueError):
                lhs, operator, rhs = expr.deconstruct()[1]
                l_field = self.resolve_output_field(lhs)
                r_field = self.resolve_output_field(rhs)
                if not l_field:
                    return r_field
                if not r_field:
                    return l_field
                if operator in ("+", "*", "/", "^"):
                    from django.db.models.fields import PositiveIntegerRelDbTypeMixin

                    if isinstance(
                        l_field, PositiveIntegerRelDbTypeMixin
                    ) and isinstance(r_field, PositiveIntegerRelDbTypeMixin):
                        return l_field
                if operator in ("+", "-", "*", "/", "^"):
                    if isinstance(l_field, models.FloatField) or isinstance(
                        r_field, models.FloatField
                    ):
                        return models.FloatField()
                    if isinstance(l_field, models.DecimalField) or isinstance(
                        r_field, models.DecimalField
                    ):
                        return models.DecimalField()
                    if isinstance(l_field, models.IntegerField) and isinstance(
                        r_field, models.IntegerField
                    ):
                        return models.IntegerField()
                return l_field or r_field
        elif isinstance(expr, exp.BaseExpression):
            if isinstance(expr, exp.Count):
                return models.PositiveBigIntegerField()
            try:
                return expr.output_field
            except (exc.FieldError, AttributeError, TypeError, ValueError):
                pass
            if isinstance(expr, exp.Aggregate):
                # fallback
                return models.FloatField()
        # applied for exp.F()  Combinable, not instance of BaseExpression
        name = self.field_adaptor_cls.get_exp_field(expr)
        if not name:
            return None
        field = self.get_field(name)
        if not field:
            return None
        output_field = field.field
        if field.transform_name:
            trans_field = constant.TRANSFORM_OUTPUT_TYPES.get(field.transform_name)
            if trans_field:
                output_field = trans_field
        # Avg, Variance and StdDev is handled by NumericOutputFieldMixin
        return output_field

    def check_query_expression(self, expr):
        return isinstance(expr, (exp.BaseExpression, exp.Combinable))

    def check_expressions(self, expr):
        try:
            _ = self.get_queryset().values(_=expr)
        except exc.FieldError as e:
            raise exc.FieldError(f"Invalid expression field {repr(expr)}: {e}")

    def check_query(self, q):
        if not isinstance(q, (models.Q, models.QuerySet, list, dict)):
            raise TypeError(f'Invalid query: {q}')
        try:
            self.get_queryset(q)
        except exc.FieldError as e:
            raise exc.FieldError(f"Invalid query {q}: {e}")

    def check_order(self, f):
        try:
            self.get_queryset().order_by(f)
        except exc.FieldError as e:
            raise exc.FieldError(f"Invalid order field {repr(f)}: {e}")

    def is_sub_model(self, model):
        if isinstance(model, DjangoModelAdaptor):
            return issubclass(self.model, model.model)
        elif isinstance(model, type) and issubclass(model, models.Model):
            return issubclass(self.model, model)
        return False

    # QUERY METHODS --------------------------------------------
    def get_instance_recursively(self, query=None, pk=None, using: str = None):
        inst = self.query(query, pk=pk, using=using).get_instance()
        if inst:
            return inst
        for parent, field in self.meta.parents.items():
            inst = self.__class__(parent).get_instance_recursively(
                query, pk=pk, using=using
            )
            if inst:
                return inst
        return None

    async def aget_instance_recursively(self, query=None, pk=None, using: str = None):
        inst = await self.query(query, pk=pk, using=using).aget_instance()
        if inst:
            return inst
        for parent, field in self.meta.parents.items():
            inst = await self.__class__(parent).aget_instance_recursively(
                query, pk=pk, using=using
            )
            if inst:
                return inst
        return None

    def get_queryset(self, query=None, pk=None, using: str = None):
        q = None
        qs = None
        if isinstance(query, list):
            q = models.Q(pk__in=[getattr(obj, "pk", obj) for obj in query])
        elif isinstance(query, dict):
            q = models.Q(**query)
        elif isinstance(query, models.Q):
            q = query
        elif isinstance(query, models.QuerySet):
            if query.model == self.model:
                qs = query
            elif issubclass(query.model, self.model) or isinstance(self.model, query.model):
                q = models.Q(pk__in=query.values('pk'))
            else:
                raise TypeError(f'Invalid queryset {type(query)}, '
                                f'queryset of {self.model} expected, got {query.model}')

        args = (q,) if q else ()
        if qs is None:
            try:
                qs = self.model.objects.all()
            except AttributeError:
                # swapped?
                qs = self.queryset_cls(self.model)
        if using:
            qs = qs.using(using)
        if args:
            qs = qs.filter(*args)
        if pk:
            qs = qs.filter(pk=pk)
        return qs

    def query(self, query=None, pk=None, using: str = None) -> DjangoModelQueryAdaptor:
        return self.query_adaptor_cls(
            self.get_queryset(query, pk=pk, using=using), model=self
        )

    def filter(self, query=None, pk=None, **filters) -> DjangoModelQueryAdaptor:
        qs = self.query(query, pk=pk)
        if filters:
            qs = qs.filter(**filters)
        return qs

    def save(self, updates: dict = None, **kwargs):
        raise NotImplementedError
