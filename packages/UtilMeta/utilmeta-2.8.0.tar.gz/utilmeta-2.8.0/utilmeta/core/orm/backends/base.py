from utilmeta.utils.adaptor import BaseAdaptor
from typing import Tuple, Optional, List, Callable, Type
from utype import Rule
from ..generator import BaseQuerysetGenerator
from ..compiler import BaseQueryCompiler

__all__ = ["ModelQueryAdaptor", "ModelAdaptor", "ModelFieldAdaptor"]


class ModelFieldAdaptor(BaseAdaptor):
    @classmethod
    def reconstruct(cls, adaptor: "BaseAdaptor"):
        pass

    __backends_route__ = "backends"
    model_adaptor_cls = None

    # hold a model field or expression
    def __init__(
        self,
        field,
        model: "ModelAdaptor" = None,
        transform_name: str = None,
        query_lookup: str = None,
        query_name: str = None,
    ):
        self.field = field
        self.transform_name = transform_name
        self.query_lookup = query_lookup
        self.query_name = query_name
        self._model = model

    @property
    def serializable(self):
        return not self.query_lookup

    @property
    def title(self) -> Optional[str]:
        return None

    @property
    def description(self) -> Optional[str]:
        return None

    @property
    def related_model(self) -> Optional["ModelAdaptor"]:
        raise NotImplementedError

    @property
    def remote_field(self) -> Optional["ModelFieldAdaptor"]:
        raise NotImplementedError

    # @property
    # def remote_is_pk(self) -> Optional['ModelFieldAdaptor']:
    #     return self.remote_field and self.remote_field.is_pk

    @property
    def reverse_lookup(self) -> Tuple[str, str]:
        return self.model.get_reverse_lookup(self.query_name)

    @property
    def target_field(self) -> Optional["ModelFieldAdaptor"]:
        raise NotImplementedError

    @property
    def through_model(self) -> Optional["ModelAdaptor"]:
        raise NotImplementedError

    @property
    def through_fields(
        self,
    ) -> Tuple[Optional["ModelFieldAdaptor"], Optional["ModelFieldAdaptor"]]:
        raise NotImplementedError

    @property
    def model(self):
        return self._model

    @property
    def field_model(self):
        raise NotImplementedError

    @property
    def rule(self) -> Type[Rule]:
        raise NotImplementedError

    @property
    def name(self) -> str:
        raise NotImplementedError

    @property
    def column_name(self) -> str:
        raise NotImplementedError

    @property
    def to_field(self) -> str:
        raise NotImplementedError

    @property
    def relate_name(self) -> str:
        raise NotImplementedError

    def get_supported_operators(self):
        pass

    @property
    def is_nullable(self):
        raise NotImplementedError

    @property
    def is_optional(self):
        raise NotImplementedError

    @property
    def is_auto(self):
        raise NotImplementedError

    @property
    def is_auto_now(self):
        raise NotImplementedError

    @property
    def is_writable(self):
        raise NotImplementedError

    @property
    def is_unique(self):
        raise NotImplementedError

    @property
    def is_db_index(self):
        raise NotImplementedError

    @property
    def is_exp(self):
        raise NotImplementedError

    @property
    def is_pk(self):
        raise NotImplementedError

    @property
    def is_fk(self):
        raise NotImplementedError

    @property
    def is_concrete(self):
        raise NotImplementedError

    @property
    def is_m2m(self):
        raise NotImplementedError

    @property
    def is_m2(self):
        raise NotImplementedError

    @property
    def is_2m(self):
        raise NotImplementedError

    @property
    def is_o2(self):
        raise NotImplementedError

    @property
    def is_2o(self):
        raise NotImplementedError

    @property
    def is_many(self):
        return self.is_2m or self.is_m2

    @property
    def is_combined(self):
        raise NotImplementedError

    @property
    def multi_relations(self):
        raise NotImplementedError

    @classmethod
    def get_exp_field(cls, exp) -> Optional[str]:
        raise NotImplementedError

    @classmethod
    def iter_combined_expression(cls, exp):
        raise NotImplementedError

    def get_lookup(self, lookup: str):
        raise NotImplementedError


class ModelQueryAdaptor(BaseAdaptor):
    queryset_cls = None

    def __init__(self, queryset, model: "ModelAdaptor"):
        self.queryset = queryset
        self.model = model

    @property
    def using(self) -> str:
        raise NotImplementedError

    @classmethod
    def get_kwargs(cls, d=None, **kwargs):
        if isinstance(d, dict):
            kwargs.update(d)
        return kwargs

    @property
    def is_sliced(self) -> bool:
        raise NotImplementedError

    def filter(self, *args, **kwargs) -> "ModelQueryAdaptor":
        raise NotImplementedError

    def count(self) -> int:
        raise NotImplementedError

    async def acount(self) -> int:
        raise NotImplementedError

    def exists(self) -> bool:
        raise NotImplementedError

    async def aexists(self) -> bool:
        raise NotImplementedError

    def update(self, d=None, **data):
        raise NotImplementedError

    async def aupdate(self, d=None, **data):
        raise NotImplementedError

    def create(self, d=None, **data):
        raise NotImplementedError

    def update_or_create(self, defaults: dict = None, **data):
        raise NotImplementedError

    async def acreate(self, d=None, **data):
        raise NotImplementedError

    async def aupdate_or_create(self, defaults: dict = None, **data):
        raise NotImplementedError

    def bulk_create(self, data: list, **kwargs):
        raise NotImplementedError

    async def abulk_create(self, data: list, **kwargs):
        raise NotImplementedError

    def bulk_update(self, data: list, fields: list):
        raise NotImplementedError

    async def abulk_update(self, data: list, fields: list):
        raise NotImplementedError

    def delete(self):
        raise NotImplementedError

    async def adelete(self):
        raise NotImplementedError

    def values(self, *fields, **kwargs) -> List[dict]:
        raise NotImplementedError

    async def avalues(self, *fields, **kwargs) -> List[dict]:
        raise NotImplementedError

    def get_instance(self):
        raise NotImplementedError

    async def aget_instance(self):
        raise NotImplementedError


class ModelAdaptor(BaseAdaptor):
    field_adaptor_cls = ModelFieldAdaptor
    query_adaptor_cls = ModelQueryAdaptor
    generator_cls = BaseQuerysetGenerator
    compiler_cls = BaseQueryCompiler
    model_cls = None

    __backends_names__ = ["django", "peewee", "sqlalchemy"]

    @classmethod
    def reconstruct(cls, adaptor: "BaseAdaptor"):
        pass

    def __init__(self, model):
        if not self.qualify(model):
            raise TypeError(f"{self.__class__}: Invalid model: {model}")
        self.model = model

    @property
    def ident(self):
        return f"{self.model.__module__}.{self.model.__name__}"

    @property
    def field_errors(self) -> Tuple[Type[Exception], ...]:
        return (Exception,)

    @property
    def integrity_errors(self) -> Tuple[Type[Exception], ...]:
        return (Exception,)

    @property
    def pk_field(self) -> field_adaptor_cls:
        raise NotImplementedError

    def get_pk(self, data: dict):
        return data.get('id', None) or data.get('pk')

    def init_instance(self, pk=None, **data):
        raise NotImplementedError

    def check_subquery(self, qs):
        raise NotImplementedError

    def check_queryset(self, qs, check_model: bool = False) -> Optional[query_adaptor_cls]:
        raise NotImplementedError

    def get_model(self, qs) -> "ModelAdaptor":
        raise NotImplementedError

    @property
    def abstract(self) -> bool:
        """
        Do not corresponding to a concrete table
        """
        raise NotImplementedError

    @property
    def table_name(self) -> str:
        raise NotImplementedError

    @property
    def default_db_alias(self) -> str:
        return "default"

    def get_parents(self) -> list:
        raise NotImplementedError

    def cross_models(self, field):
        raise NotImplementedError

    def get_field(
        self,
        name: str,
        validator: Callable = None,
        silently: bool = False,
    ) -> Optional[field_adaptor_cls]:
        """
        Get name from a field references
        """
        raise NotImplementedError

    def get_backward(self, field: str) -> str:
        raise NotImplementedError

    def get_reverse_lookup(self, lookup: str) -> Tuple[str, Optional[str]]:
        raise NotImplementedError

    def get_last_many_relates(self, lookup: str):
        raise NotImplementedError

    def get_fields(self, many=False, no_inherit=False) -> List[ModelFieldAdaptor]:
        raise NotImplementedError

    def get_related_adaptor(self, field):
        return self.__class__(field.related_model) if field.related_model else None

    def gen_lookup_keys(
        self, field: str, keys, strict: bool = True, excludes: List[str] = None
    ) -> list:
        raise NotImplementedError

    def gen_lookup_filter(self, field, q, excludes: List[str] = None):
        raise NotImplementedError

    def include_many_relates(self, field: str):
        raise NotImplementedError

    def resolve_output_field(self, expr):
        raise NotImplementedError

    def check_query_expression(self, expr):
        raise NotImplementedError

    def check_expressions(self, expr):
        pass

    def check_query(self, q):
        pass

    def check_order(self, f):
        pass

    def is_sub_model(self, model):
        raise NotImplementedError

    def query(self, query=None, pk=None, using: str = None) -> ModelQueryAdaptor:
        raise NotImplementedError

    def filter(self, query=None, pk=None, **filters) -> ModelQueryAdaptor:
        raise NotImplementedError

    def get_queryset(self, query=None, pk=None, using: str = None):
        # for django it's like model.objects.all()
        raise NotImplementedError

    def save(
        self,
        filters: dict = None,
        updates: dict = None,
    ):
        raise NotImplementedError

    # ------------- QUERY METHODS
    def get_instance_recursively(self, query=None, pk=None, using: str = None):
        raise NotImplementedError

    async def aget_instance_recursively(self, query=None, pk=None, using: str = None):
        raise NotImplementedError
