from utype.parser.cls import ClassParser
from .fields.field import ParserQueryField
from .fields.filter import ParserFilter
from utilmeta.core.orm import exceptions
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .compiler import BaseQueryCompiler
    from .generator import BaseQuerysetGenerator


class QueryClassParser(ClassParser):
    parser_field_cls = ParserFilter

    def __init__(self, obj, *args, **kwargs):
        model = getattr(obj, "__model__", None)
        from .backends.base import ModelAdaptor

        self.model = ModelAdaptor.dispatch(model) if model else None
        super().__init__(obj, *args, **kwargs)

    @property
    def kwargs(self):
        return dict(model=self.model)

    def get_generator(
        self, values: dict, using: str = None, **kwargs
    ) -> "BaseQuerysetGenerator":
        return self.model.generator_cls(self, values, using=using, **kwargs)

    @property
    def schema_annotations(self):
        data = super().schema_annotations or {}
        if self.model:
            data.update(model=self.model.ident)
        return data


class SchemaClassParser(ClassParser):
    parser_field_cls = ParserQueryField

    def __init__(self, obj, *args, **kwargs):
        model = getattr(obj, "__model__", None)
        from .backends.base import ModelAdaptor

        self.model: ModelAdaptor = ModelAdaptor.dispatch(model) if model else None
        super().__init__(obj, *args, **kwargs)

        serialize_options = getattr(obj, "__serialize_options__", None)
        self.output_options = (
            self.options_cls.generate_from(serialize_options)
            if serialize_options
            else None
        )

        pk_names = set()
        if self.model:
            for name in list(self.fields):
                field = self.fields[name]
                if isinstance(field, ParserQueryField):
                    if field.primary_key:
                        pk_names.add(name)
                    if not field.model:
                        # maybe the base class only use (orm.Schema) as base and not specifying model
                        # we need to assign and setup here, otherwise
                        # we should regenerate another new instance to avoid model conflict
                        try:
                            field = field.reconstruct(self.model)
                            field.setup(self.options)
                        except Exception as e:
                            raise e.__class__(
                                f"{self.name}(orm.Schema): setup field [{repr(name)}] "
                                f"for model: {self.model} failed with error: {e}"
                            ) from e

                        self.fields[name] = field
            # if pk_names:
            #     pass
            # else:
            #     if self.options.mode and 'w' in self.options.mode:
            #         raise exceptions.InvalidSchema(f'{self.name}(orm.Schema): with mode: {repr(self.options.mode)}) '
            #                                        f'requires to declare a primary key field (such as id)')

        self.pk_names = pk_names

    @property
    def kwargs(self):
        return dict(model=self.model)

    def get_compiler(self, queryset, context=None) -> "BaseQueryCompiler":
        if not self.model:
            raise exceptions.ModelRequired(
                f"{self.name}: model is required for query execution"
            )
        return self.model.compiler_cls(self, queryset, context=context)

    def get_instance(self, data: dict):
        # pk = self.get_pk(data)
        inst = dict(pk=getattr(data, "pk", None))
        for key, val in data.items():
            field = self.get_field(key)
            if isinstance(field, ParserQueryField):
                if field.model_field.is_concrete:
                    inst[field.model_field.column_name] = val
        return self.model.init_instance(**inst)

    def get_pk(self, data: dict):
        for name in self.pk_names:
            pk = data.get(name, data.__dict__.get(name))
            if pk is not None:
                return pk

    @property
    def schema_annotations(self):
        data = super().schema_annotations or {}
        if self.model:
            data.update(model=self.model.ident)
        return data

    @classmethod
    def valid_schema(cls, schema_cls):
        if isinstance(schema_cls, type):
            parser_cls = getattr(schema_cls, "__parser_cls__", None)
            parser = getattr(schema_cls, "__parser__", None)
            if parser and isinstance(parser, cls):
                return True
            if (
                parser_cls
                and isinstance(parser_cls, type)
                and issubclass(parser_cls, cls)
            ):
                return True
        return False
