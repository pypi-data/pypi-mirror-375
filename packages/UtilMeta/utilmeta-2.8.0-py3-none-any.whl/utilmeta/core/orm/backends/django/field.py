from utype.types import Self
from utilmeta.utils import multi
from ..base import ModelFieldAdaptor
from typing import Union, Optional, Type, TYPE_CHECKING, Tuple, Any
from django.db import models
from django.db.models.fields.reverse_related import ForeignObjectRel
from django.db.models.query_utils import DeferredAttribute
from . import constant
from . import expressions as exp
from utype import Rule, Lax
from utype import types
from functools import cached_property

if TYPE_CHECKING:
    from .model import DjangoModelAdaptor


def one_to(field):
    return isinstance(
        field, (models.OneToOneField, models.ForeignKey, models.OneToOneRel)
    )


def many_to(field):
    if isinstance(field, models.OneToOneRel):
        # OneToOneRel is subclass of ManyToOneRel
        return False
    return isinstance(
        field, (models.ManyToManyField, models.ManyToManyRel, models.ManyToOneRel)
    )


def to_many(field):
    return isinstance(
        field, (models.ManyToManyField, models.ManyToManyRel, models.ForeignKey)
    )


def to_one(field):
    return isinstance(
        field, (models.OneToOneField, models.OneToOneRel, models.ManyToOneRel)
    )


class DjangoModelFieldAdaptor(ModelFieldAdaptor):
    field: Union[models.Field, ForeignObjectRel, exp.BaseExpression, exp.Combinable]
    model: "DjangoModelAdaptor"

    def __init__(
        self, field,
        model: "DjangoModelAdaptor" = None,
        transform_name: str = None,
        query_lookup: str = None,
        query_name: str = None,
    ):
        if isinstance(field, DeferredAttribute):
            field = field.field
            field_name = getattr(field, "field_name", getattr(field, "name", None))
            if not query_name:
                fields = [field_name]
                if transform_name:
                    fields.append(transform_name)
                if query_lookup:
                    fields.append(query_lookup)
                query_name = '__'.join(fields)

        if not self.qualify(field):
            raise TypeError(f"Invalid field: {field}")

        super().__init__(
            field, model=model,
            transform_name=transform_name,
            query_name=query_name,
            query_lookup=query_lookup
        )

    @property
    def multi_relations(self):
        return self.query_name and "__" in self.query_name

    # @classmethod
    # def allow_arbitrary_transform(cls, field):
    #     from django.db.models import JSONField
    #     fields = [JSONField]
    #     try:
    #         from django.contrib.postgres.fields import JSONField as _pgJSONField
    #         fields.append(_pgJSONField)
    #     except ImportError:
    #         pass
    #     return isinstance(field, tuple(fields))

    @property
    def title(self) -> Optional[str]:
        name = self.field.verbose_name
        if name != self.field.name:
            return str(name)
        return None

    @property
    def description(self) -> Optional[str]:
        return str(self.field.help_text or "") or None

    @classmethod
    def qualify(cls, obj):
        return isinstance(
            obj, (models.Field, ForeignObjectRel, exp.BaseExpression, exp.Combinable)
        )

    @property
    def field_model(self):
        if self.is_exp:
            return None
        return getattr(self.field, "model", None)

    @property
    def target_field(self) -> Optional["ModelFieldAdaptor"]:
        target_field = getattr(self.field, "target_field", None)
        if target_field:
            return self.__class__(target_field, model=self.model)
        return None

    @property
    def remote_field(self) -> Optional["ModelFieldAdaptor"]:
        remote_field = getattr(self.field, "remote_field", None)
        if remote_field and self.field.related_model:
            return self.__class__(remote_field, model=self.field.related_model)
        return None

    @property
    def related_model(self):
        if self.is_exp:
            return None
        rel = getattr(self.field, "related_model")
        if rel:
            if rel == "self":
                return self
            from .model import DjangoModelAdaptor
            if not DjangoModelAdaptor.qualify(rel):
                raise TypeError(f'Invalid related model: {rel} for field: {self.model.model}.{repr(self.name)}')
            return DjangoModelAdaptor(rel)
        return None

    @property
    def through_model(self):
        if not self.is_m2m:
            return None
        if isinstance(self.field, models.ManyToManyField):
            rel = self.field.remote_field
        else:
            rel = self.field
        if rel.through:
            from .model import DjangoModelAdaptor

            return DjangoModelAdaptor(rel.through)
        return None

    @property
    def through_fields(
        self,
    ) -> Tuple[Optional["ModelFieldAdaptor"], Optional["ModelFieldAdaptor"]]:
        if not self.is_m2m:
            return None, None
        is_rel = False
        related_model = self.related_model
        through_model = self.through_model
        if not related_model or not through_model:
            return None, None
        if isinstance(self.field, models.ManyToManyField):
            rel = self.field.remote_field
        else:
            rel = self.field
            is_rel = True
        if rel.through_fields:
            _from = through_model.get_field(rel.through_fields[0])
            _to = through_model.get_field(rel.through_fields[1])
        else:
            _from = _to = None
            for field in through_model.get_fields(many=False, no_inherit=True):
                if not field.related_model:
                    continue
                if issubclass(field.related_model.model, self.model.model):
                    _from = field
                elif issubclass(field.related_model.model, related_model.model):
                    _to = field
        return (_to, _from) if is_rel else (_from, _to)

    @property
    def is_nullable(self):
        if not self.is_concrete:
            return True
        return getattr(self.field, "null", False)

    @property
    def is_optional(self):
        if not self.is_concrete:
            return True
        return self.field.default != models.NOT_PROVIDED or self.is_auto

    @property
    def is_writable(self):
        if not self.is_concrete:
            return False
        if self.field == self.model.meta.auto_field:
            return False
        param = self.params
        auto_now_add = param.get("auto_now_add")
        auto_created = param.get("auto_created")
        if auto_now_add or auto_created:
            return False
        return True

    @property
    def is_unique(self):
        if not self.is_concrete:
            return False
        return self.field.unique

    @property
    def is_db_index(self):
        if not self.is_concrete:
            return False
        return self.field.db_index

    @property
    def is_auto(self):
        if not self.is_concrete:
            return False
        param = self.params
        auto_now_add = param.get("auto_now_add")
        auto_now = param.get("auto_now")
        auto_created = param.get("auto_created")
        if auto_now_add or auto_now or auto_created:
            return True
        return self.field == self.model.meta.auto_field

    @property
    def is_auto_now(self):
        if not self.is_concrete:
            return False
        param = self.params
        auto_now = param.get("auto_now")
        return auto_now

    @classmethod
    def _get_type(cls, field: models.Field) -> Optional[type]:
        if not isinstance(field, models.Field):
            return None
        _t = field.get_internal_type()
        for fields, t in constant.FIELDS_TYPE.items():
            if _t in fields:
                return t
        return None

    @classmethod
    def _get_params(cls, field: models.Field) -> dict:
        if not isinstance(field, models.Field):
            return {}
        return field.deconstruct()[3] or {}

    @property
    def type(self) -> type:
        return self._get_type(self.field)

    @property
    def params(self) -> dict:
        return self._get_params(self.field)

    @cached_property
    def rule(self) -> Type[Rule]:
        _type = None
        _args = []
        field = self.field

        if self.query_lookup:
            _type = constant.LOOKUP_TYPE_MAP.get(self.query_lookup)
            if _type == Self:
                _type = self._get_type(self.field)
            field = None

        elif self.transform_name:
            _type = constant.TRANSFORM_TYPE_MAP.get(self.transform_name)
            field = None

        elif self.is_o2:
            mod = self.related_model
            if mod:
                _type = mod.pk_field.rule

                if not _type.__args__ and not _type.__validators__:
                    _type = _type.__origin__

                if _type and self.is_nullable:
                    from utype.parser.rule import LogicalType

                    _type = LogicalType.any_of(_type, type(None))

                # return _type

        elif self.is_concrete:
            _type = self._get_type(self.field)

            if _type != Any:
                if _type and self.is_nullable:
                    from utype.parser.rule import LogicalType

                    _type = LogicalType.any_of(_type, type(None))

        elif self.is_exp:
            if isinstance(self.field, exp.Count):
                # shortcut for Count: do not set le limit
                return types.NaturalInt
            field = self.model.resolve_output_field(self.field)
            _type = self._get_type(field) if field else None

        elif self.is_many:
            _type = list
            target_field = self.target_field
            if target_field:
                _args = [target_field.rule]
            field = None

        else:
            try:
                from django.contrib.postgres.fields import ArrayField
            except (ImportError, ModuleNotFoundError):
                # required psycopg2
                pass
            else:
                if isinstance(field, ArrayField):
                    _type = list
                    if field.base_field:
                        base_field = self.__class__(field.base_field, model=self.model)
                        _args = [base_field.rule]

        kwargs = {}

        if field:
            if _type == bool:
                params = {}
                # requires no params
            else:
                params = self._get_params(field)

            if params.get("max_length"):
                kwargs["max_length"] = params["max_length"]
            if params.get("min_length"):
                kwargs["min_length"] = params["min_length"]
            if "max_value" in params:
                kwargs["le"] = params["max_value"]
            if "min_value" in params:
                kwargs["ge"] = params["min_value"]

            if isinstance(field, models.DecimalField):
                kwargs["max_length"] = field.max_digits
                kwargs["decimal_places"] = Lax(field.decimal_places)
            # for the reason that IntegerField is the base class of All integer fields
            # so the isinstance determine will be the last to include
            elif isinstance(field, models.IntegerField):
                if isinstance(field, models.PositiveSmallIntegerField):
                    kwargs["ge"] = 0
                    kwargs["le"] = constant.SM
                elif isinstance(field, models.PositiveBigIntegerField):
                    kwargs["ge"] = 0
                    kwargs["le"] = constant.LG
                elif isinstance(field, models.PositiveIntegerField):
                    kwargs["ge"] = 0
                    kwargs["le"] = constant.MD
                elif isinstance(field, models.BigAutoField):
                    kwargs["ge"] = 1
                    kwargs["le"] = constant.LG
                elif isinstance(field, models.AutoField):
                    kwargs["ge"] = 1
                    kwargs["le"] = constant.MD
                elif isinstance(field, models.BigIntegerField):
                    kwargs["ge"] = -constant.LG
                    kwargs["le"] = constant.LG
                elif isinstance(field, models.SmallIntegerField):
                    kwargs["ge"] = -constant.SM
                    kwargs["le"] = constant.SM
                else:
                    kwargs["ge"] = -constant.MD
                    kwargs["le"] = constant.MD

        if _type is None:
            # fallback to string field
            _type = str

        if not _args and not kwargs and isinstance(_type, type) and issubclass(_type, Rule):
            # shortcut
            return _type

        return Rule.annotate(_type, *_args, constraints=kwargs)

    @property
    def name(self) -> Optional[str]:
        if self.is_exp:
            return None
        if hasattr(self.field, "name"):
            return self.field.name
        if hasattr(self.field, "field_name"):
            # toOneRel
            return self.field.field_name
        return None

    @property
    def column_name(self) -> Optional[str]:
        if isinstance(self.field, models.Field):
            return self.field.column
        return None

    @property
    def to_field(self) -> Optional[str]:
        if self.is_fk:
            field: models.ForeignKey = self.field   # noqa
            try:
                return field.to_fields[0]
            except IndexError:
                pass
        return None

    @property
    def relate_name(self) -> Optional[str]:
        if self.is_fk:
            related_name = getattr(self.field, "_related_name", None)
            if related_name:
                return related_name
            try:
                return (
                    self.field.remote_field.name
                    or self.field.remote_field.get_cache_name()
                )
            except (AttributeError, NotImplementedError):
                return None
        return None

    def get_supported_operators(self):
        pass

    @property
    def is_exp(self):
        return isinstance(self.field, (exp.BaseExpression, exp.Combinable))

    @property
    def is_combined(self):
        return isinstance(self.field, exp.CombinedExpression)

    @property
    def is_rel(self):
        return isinstance(self.field, ForeignObjectRel)

    @property
    def is_pk(self):
        return isinstance(self.field, models.Field) and self.field.primary_key

    @property
    def is_fk(self):
        return isinstance(self.field, models.ForeignKey)

    @property
    def is_concrete(self):
        if self.is_exp:
            return False
        if self.is_m2m:
            # somehow ManyToManyField is considered "concrete" in django
            return False
        return getattr(self.field, "concrete", False)

    @property
    def is_m2m(self):
        return isinstance(self.field, (models.ManyToManyField, models.ManyToManyRel))

    @property
    def is_m2(self):
        return many_to(self.field)

    @property
    def is_2m(self):
        return to_many(self.field)

    @property
    def is_o2(self):
        return one_to(self.field)

    @property
    def is_2o(self):
        return to_one(self.field)

    @classmethod
    def get_exp_field(cls, expr) -> Optional[str]:
        if isinstance(expr, str):
            return expr
        if isinstance(expr, exp.CombinedExpression):
            return None
        if isinstance(expr, exp.F):
            return expr.name
        if not isinstance(expr, exp.BaseExpression):
            return None
        try:
            name = expr.deconstruct()[1][0]  # noqa
            if isinstance(name, exp.BaseExpression):  # maybe F
                return cls.get_exp_field(name)  # noqa
            if not isinstance(name, str):
                return None
            return name
        except (ValueError, IndexError, AttributeError):
            return None

    @classmethod
    def iter_combined_expression(cls, expr):
        if isinstance(expr, exp.CombinedExpression):
            exps = expr.deconstruct()[1]
            if multi(exps):
                for e in exps:
                    for i in cls.iter_combined_expression(e):
                        yield i
        elif isinstance(exp, (exp.BaseExpression, exp.Combinable)):
            yield exp
        return

    def get_lookup(self, lookup: str):
        return self.field.get_lookup(lookup)
