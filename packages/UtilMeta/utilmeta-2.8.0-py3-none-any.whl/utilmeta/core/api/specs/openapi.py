"""
Implement OpenAPI document generation
"""
import inspect
import warnings

import utype.utils.exceptions

from ..endpoint import Endpoint
from utilmeta.core.api.base import API
from utilmeta.core.api.route import APIRoute
from utilmeta.core.request import properties
from utilmeta.core.response import Response
from utilmeta.core.auth.base import BaseAuthentication
from utilmeta.core.file.base import File
from utilmeta.core.auth.properties import User
from utilmeta.core.response.base import Headers, JSON, OCTET_STREAM, PLAIN
from utilmeta.utils.context import Property, ParserProperty
from utilmeta.utils.constant import HAS_BODY_METHODS, HTTP_METHODS
from utilmeta.utils import (
    valid_url,
    json_dumps,
    get_origin,
    file_like,
    multi,
    url_join,
    requires,
)
from utilmeta.conf import Preference
from utype import Schema, Field, JsonSchemaGenerator
from utype.parser.field import ParserField
from utype.parser.rule import LogicalType
from utype.utils.datastructures import unprovided
from utype.utils.functional import get_obj_name
from typing import Type, Tuple, Dict, List, Union, TYPE_CHECKING, Optional, Callable
from .base import BaseAPISpec
import os
import json
import re
import copy


if TYPE_CHECKING:
    from utilmeta import UtilMeta

MULTIPART = "multipart/form-data"


def guess_content_type(schema: dict):
    if not schema:
        return None

    type = schema.get("type")
    format = schema.get("format")
    conditions = schema.get('anyOf') or schema.get('allOf') or schema.get('oneOf')

    if type in ("object", "array"):
        return JSON

    if schema.get("$ref"):
        return JSON

    if format == "binary":
        return OCTET_STREAM

    if isinstance(conditions, list):
        for cond in conditions:
            ct = guess_content_type(cond)
            if ct:
                return ct

    return None


def get_operation_id(
    method: str, path: str, excludes: list = (), attribute: bool = False
):
    ident = f'{method.lower()}:{path.strip("/")}'
    if attribute:
        ident = re.sub("[^A-Za-z0-9]+", "_", ident).strip("_")
    if excludes:
        i = 1
        origin = ident
        while ident in excludes:
            ident = f"{origin}_{i}"
            i += 1
    return ident


def get_docs_from_url(url, timeout: int = None):
    if not valid_url(url, raise_err=False):
        return None
    from urllib.request import urlopen
    from http.client import HTTPResponse

    try:
        resp: HTTPResponse = urlopen(url, timeout=timeout)
    except Exception as e:
        warnings.warn(f"parse external docs url: {url} failed: {e}")
        return None
    if resp.status == 200:
        content_type = resp.getheader("Content-Type") or ""
        if "yaml" in content_type or "yml" in content_type:
            requires(yaml="pyyaml")
            import yaml

            obj = yaml.safe_load(resp.read())
        else:
            obj = json.loads(resp.read())
    else:
        return None
    resp.close()
    return obj


def normalize_dict(data: dict, key_orders: list):
    data: dict = json.loads(json_dumps(data))
    sorted_dict = {}
    for key in key_orders:
        if key in data:
            sorted_dict[key] = data[key]

    # 添加原始字典中存在但未在顺序中指定的键（按原始顺序）
    for key, val in data.items():
        if key not in sorted_dict:
            sorted_dict[key] = val

    return sorted_dict


class OpenAPIGenerator(JsonSchemaGenerator):
    DEFAULT_REF_PREFIX = "#/components/schemas/"

    def generate_for_field(self, f: ParserField, options=None, **kwargs):
        data = super().generate_for_field(f, options=options, **kwargs)
        if data is None:
            return data
        t = f.output_type if self.output else f.type
        if isinstance(t, type) and issubclass(t, File):
            data.update(accept=t.accept)
        if isinstance(t, LogicalType) and f.discriminator_map:
            # not part of json-schema, but in OpenAPI
            data.update(
                discriminator=dict(
                    propertyName=f.field.discriminator,
                    mapping={
                        k: self.generate_for_type(v)
                        for k, v in f.discriminator_map.items()
                    },
                )
            )
        return data

    def get_ref_object(self, ref: str):
        name = ref.lstrip(self.ref_prefix)
        return self.names.get(name)

    def get_ref_schema(self, ref: str):
        obj = self.get_ref_object(ref)
        return self.defs.get(obj)

    def get_schema(self, schema: dict):
        if not schema or not isinstance(schema, dict):
            return None
        ref = schema.get("$ref")
        if ref:
            return self.get_ref_schema(ref)
        return schema

    def get_body_content_type(self, body_schema: dict):
        if not body_schema or not isinstance(body_schema, dict):
            return None
        ref = body_schema.get("$ref")
        if ref:
            body_schema = self.get_ref_schema(ref)
            if not body_schema or not isinstance(body_schema, dict):
                return None
        if body_schema.get("type") == "object":
            for key, field in body_schema.get("properties", {}).items():
                if field.get("format") == "binary":
                    return MULTIPART
                if field.get("type") == "array":
                    if field.get("items", {}).get("format") == "binary":
                        return MULTIPART
            return JSON

        return guess_content_type(body_schema)

    def generate_for_response(self, response: Type[Response]):
        parser = getattr(response, "__parser__", None)
        result_field = parser.get_field("result") if parser else None
        headers_field = parser.get_field("headers") if parser else None
        example = getattr(response, 'example', None)

        result_schema = self.generate_for_field(result_field) if result_field else None
        headers_schema = (
            self.__class__(headers_field.type, output=True)()
            if headers_field and headers_field.type != Headers
            else {}
        )
        # headers is different, doesn't need to generate $ref

        headers_props = headers_schema.get("properties") or {}
        headers_required = headers_schema.get("required") or []
        headers = {}
        for key, val_schema in headers_props.items():
            headers[key] = {"schema": val_schema, "required": key in headers_required}

        content_type = response.content_type
        # todo: headers wrapped
        if response.wrapped:
            props = {}
            keys = {}
            if response.result_key:
                props[response.result_key] = result_schema
                keys.update({"x-response-result-key": response.result_key})
            if response.message_key:
                msg = dict(self.generate_for_type(str))
                msg.update(
                    title="Message",
                    description="an error message of response",
                )
                props[response.message_key] = msg
                keys.update({"x-response-message-key": response.message_key})
            if response.state_key:
                state = dict(self.generate_for_type(str))
                state.update(
                    title="State",
                    description="action state code of response",
                )
                props[response.state_key] = state
                keys.update({"x-response-state-key": response.state_key})
            if response.count_key:
                cnt = dict(self.generate_for_type(int))
                cnt.update(
                    title="Count",
                    description="a count of the total number of query result",
                )
                props[response.count_key] = cnt
                keys.update({"x-response-count-key": response.count_key})

            data_schema = {
                "type": "object",
                "properties": props,
                "required": list(props),
            }
            if keys:
                data_schema.update(keys)
            content_type = JSON
        else:
            data_schema = result_schema
            if not content_type:
                content_type = guess_content_type(data_schema) or JSON

        content_data = {
            "schema": data_schema
        }
        if example is not None:
            content_data["example"] = example

        response_schema = dict(
            content={content_type: content_data},
        )
        if headers:
            response_schema.update(headers=headers)
        if response.description:
            response_schema.update(description=response.description)
        if response.name:
            response_schema.update({"x-response-name": response.name})

        return response_schema


class OpenAPIInfo(Schema):
    title: str
    version: str
    description: str = Field(default="")
    term_of_service: str = Field(alias="termsOfService", alias_from=["tos"], default="")
    contact: dict = Field(default_factory=dict)
    license: dict = Field(default_factory=dict)


class ServerSchema(Schema):
    url: str
    description: str = Field(default="")
    variables: dict = Field(default_factory=dict)


class ComponentsSchema(Schema):
    schemas: dict = Field(default_factory=dict, defer_default=True)
    responses: dict = Field(default_factory=dict, defer_default=True)
    parameters: dict = Field(default_factory=dict, defer_default=True)
    examples: dict = Field(default_factory=dict, defer_default=True)
    requestBodies: dict = Field(default_factory=dict, defer_default=True)
    headers: dict = Field(default_factory=dict, defer_default=True)
    securitySchemes: dict = Field(default_factory=dict, defer_default=True)
    links: dict = Field(default_factory=dict, defer_default=True)
    callbacks: dict = Field(default_factory=dict, defer_default=True)
    pathItems: dict = Field(default_factory=dict, defer_default=True)


class OpenAPISchema(Schema):
    __options__ = utype.Options(addition=True)

    openapi: str
    info: OpenAPIInfo
    paths: Dict[str, dict] = utype.Field(default_factory=dict)
    servers: List[ServerSchema] = utype.Field(default_factory=list)
    components: ComponentsSchema = utype.Field(default_factory=dict)
    security: list = utype.Field(default_factory=list)
    tags: list = utype.Field(default_factory=list)


_generated_document = None


class OpenAPI(BaseAPISpec):
    spec = "openapi"
    __version__ = "3.1.0"
    generator_cls = OpenAPIGenerator
    schema_cls = OpenAPISchema
    FORMATS = ["json", "yaml"]
    PARAMS_IN = ["path", "query", "header", "cookie"]
    URL_FETCH_TIMEOUT = 5
    FIELD_ORDERS = [
        'openapi',
        'info',
        'jsonSchemaDialect',
        'servers',
        'paths',
        'webhooks',
        'components',
        'security',
        'tags',
        'externalDocs'
    ]
    OPERATION_FIELD_ORDERS = [
        'method', 'path', 'operationId', 'description', 'tags', 'security', 'parameters', 'requestBody', 'responses'
    ]

    # None -> dict
    # json -> json string
    # yml -> yml string

    def __init__(
        self,
        service: "UtilMeta",
        external_docs: Union[str, dict, Callable] = None,
        base_url: str = None,
        api_prefix: str = None,
    ):
        super().__init__(service)
        self.defs = {}
        self.names = {}
        self.responses = {}
        self.response_names = {}
        self.paths: Dict[str, dict] = {}
        self.security_schemas = {}
        self.operations = set()
        self.external_docs = external_docs
        self.base_url = base_url
        self.api_prefix = api_prefix
        self.pref = Preference.get()
        self.tags = {}
        # self.operations = {}

    def get_def_name(self, t: type):
        for k, v in self.names.items():
            if v == t:
                return k
        return get_obj_name(t)

    def get_defs(self) -> Dict[str, dict]:
        defs = {}
        for t, values in self.defs.items():
            name = self.get_def_name(t)
            defs[name] = values
        return defs

    def get_responses(self) -> Dict[str, dict]:
        resp = {}
        for r, values in self.responses.items():
            name = self.get_response_name(r)
            resp[name] = values
        return resp

    def merge_openapi_docs(self, *docs: dict) -> OpenAPISchema:
        components = ComponentsSchema()
        paths = {}
        additions = {}
        security = []
        tag_names = []
        tags = []
        info = None
        servers = []
        for doc in docs:
            if not isinstance(doc, OpenAPISchema):
                doc = self.schema_cls(doc)
            if not info or (not info.title and doc.info.title):
                info = doc.info
            doc_paths = doc.paths
            if not self.base_url:
                for server in doc.servers:
                    if not any(s.url == server.url for s in servers):
                        servers.append(server)
            elif doc.servers:
                server = doc.servers[0]
                if server.url != self.base_url:
                    doc_paths = self.get_rel_paths(doc_paths, server.url, self.base_url)
            else:
                # no servers: default to be the origin of current base_url
                server_url = get_origin(self.base_url)
                if server_url != self.base_url:
                    doc_paths = self.get_rel_paths(doc_paths, server_url, self.base_url)

            for key, values in doc.components.items():
                if components.get(key):
                    components[key].update(values)
                else:
                    components[key] = dict(values)

            for path, values in doc_paths.items():
                if self.api_prefix:
                    if not path.strip('/').startswith(self.api_prefix.strip('/')):
                        continue
                if path in paths:
                    paths[path].update(values)
                else:
                    paths[path] = dict(values)

            security.extend(doc.security)
            for tag in doc.tags:
                tag_name = tag.get("name") if isinstance(tag, dict) else str(tag)
                if not tag_name:
                    continue
                if tag_name in tag_names:
                    continue
                tags.append(tag_name)
                tags.append(tag if isinstance(tag, dict) else {"name": tag_name})
            for key, val in doc.items():
                if key not in self.schema_cls.__parser__.fields:
                    additions[key] = val
        return self.schema_cls(
            openapi=self.__version__,
            info=info,
            paths=paths,
            servers=[self.server] if self.base_url else servers,
            components=components,
            security=security,
            tags=tags,
            **additions,
        )

    def get_external_docs(self, external_docs) -> List[OpenAPISchema]:
        if not external_docs:
            return []
        docs = external_docs
        if callable(docs):
            try:
                docs = docs(self.service)
            except Exception as e:
                warnings.warn(
                    f"call external docs function: {external_docs} failed: {e}"
                )
                return []

        if multi(docs):
            ext_docs = []
            for doc in docs:
                ext_docs.extend(self.get_external_docs(doc))
            return ext_docs

        file = None
        if isinstance(docs, File):
            file = docs
            docs = docs.read()
        elif file_like(docs):
            file = File(docs)
            docs = file.read()

        if isinstance(docs, bytes):
            docs = docs.decode()

        if file and file.filename and isinstance(docs, str):
            if file.filename.endswith(".yaml") or file.filename.endswith(".yml"):
                requires(yaml="pyyaml")
                import yaml

                docs = yaml.safe_load(docs)

        if isinstance(docs, dict):
            try:
                return [OpenAPISchema(docs)]
            except utype.exc.ParseError as e:
                warnings.warn(f"parse external docs object failed: {e}")
                return []
        if isinstance(docs, str):
            if valid_url(docs, raise_err=False):
                obj = get_docs_from_url(docs, timeout=self.URL_FETCH_TIMEOUT)
                if not obj:
                    return []
            elif os.path.exists(docs):
                try:
                    docs_content = open(docs, "r", errors="ignore").read()
                except Exception as e:
                    warnings.warn(f"parse external docs file: {docs} failed: {e}")
                    return []
                if docs.endswith(".yaml") or docs.endswith(".yml"):
                    requires(yaml="pyyaml")
                    import yaml

                    obj = yaml.safe_load(docs_content)
                else:
                    obj = json.loads(docs_content)
            else:
                # try to load external_docs as content
                try:
                    obj = json.loads(docs)
                except json.JSONDecodeError:
                    try:
                        requires(yaml="pyyaml")
                        import yaml

                        obj = yaml.safe_load(docs)
                    except Exception as e:
                        warnings.warn(
                            f"parse external docs content failed with error: {e}"
                        )
                        return []
            if obj:
                try:
                    return [OpenAPISchema(obj)]
                except utype.exc.ParseError as e:
                    warnings.warn(f"parse external docs failed: {e}")
                    return []

        return []

    @classmethod
    def get_rel_paths(cls, paths: dict, current_base_url: str, base_url: str) -> dict:
        # current: http://127.0.0.1:8000/api
        # 1, base_url: http://127.0.0.1:8000
        # 2, base_url: http://new.location.com/some/route
        # 3, base_url: http://new.location.com
        if (
            not current_base_url
            or not base_url
            or current_base_url == base_url
            or not paths
        ):
            return paths
        prefix = ""
        prefix_strip = False
        # only support prefix
        if current_base_url.startswith(base_url):
            prefix = current_base_url[len(base_url) :]
        elif base_url.startswith(current_base_url):
            prefix = base_url[len(current_base_url) :]
            prefix_strip = True
        else:
            from urllib.parse import urlparse

            current_parsed = urlparse(current_base_url)
            url_parsed = urlparse(base_url)
            if current_parsed.path.startswith(url_parsed.path):
                prefix = current_parsed.path[len(url_parsed.path) :]
            elif url_parsed.path.startswith(current_parsed.path):
                prefix = url_parsed.path[len(current_parsed.path) :]
                prefix_strip = True
            elif current_parsed.path:
                # todo: deal with this situation
                prefix = current_parsed.path
        prefix = prefix.strip("/")

        if not prefix:
            return paths

        prefix = "/" + prefix

        new_paths = {}
        for key, path in paths.items():
            if prefix_strip:
                key = "/" + str(key).lstrip("/")
                if key == prefix or key.startswith(prefix + "/"):
                    # prefix: /api
                    # key: /api/articles -> /articles
                    #     /api/ ----------> /
                    #     /api -----------> /
                    #     /static --------> none
                    new_path = "/" + key[len(prefix) :].lstrip("/")
                else:
                    continue
            else:
                if key.strip("/"):
                    new_path = prefix + "/" + str(key).lstrip("/")
                else:
                    new_path = prefix
            new_paths[new_path] = path
        return new_paths

    def __call__(self):
        # consider merge the UtilMeta docs with the application docs
        adaptor_docs = None
        if not self.service.adaptor.backend_views_empty:
            try:
                # generated from the inner app
                docs = self.service.adaptor.generate(spec=self.spec)
                if docs:
                    adaptor_docs = OpenAPISchema(docs)
                    if not adaptor_docs.servers:
                        adaptor_docs.servers = [
                            ServerSchema(
                                url=url_join(
                                    get_origin(self.base_url),
                                    self.service.adaptor.root_path,
                                )
                            )
                        ]
            except NotImplementedError:
                adaptor_docs = None
            except Exception as e:
                warnings.warn(
                    f"generate OpenAPI docs for [{self.service.backend_name}] failed: {e}"
                )
                from utilmeta.utils import Error

                err = Error(e)
                err.setup()
                print(err.full_info)

        self.generate_paths()
        paths = self.paths
        # if self.base_url and paths:
        #     if self.service.base_url != self.base_url:
        #         paths = self.get_rel_paths(paths, self.service.base_url, self.base_url)

        utilmeta_docs = OpenAPISchema(
            openapi=self.__version__,
            info=self.generate_info(),
            components=self.components,
            paths=paths,
            tags=list(self.tags.values()),
            servers=[self.server],
        )
        docs = [utilmeta_docs]
        # even of no paths: some adaptor generate no server.url
        # if paths:
        #     docs.append(utilmeta_docs)
        if adaptor_docs:
            docs.append(adaptor_docs)
        if self.external_docs:
            docs.extend(self.get_external_docs(self.external_docs))
        if not docs:
            return utilmeta_docs
        if len(docs) == 1:
            return docs[0]
        return self.merge_openapi_docs(*docs)

    def get_generator(self, t, output: bool = False):
        return self.generator_cls(t, defs=self.defs, names=self.names, output=output)

    @property
    def components(self):
        return dict(
            schemas=self.get_defs(),
            responses=self.get_responses(),
            securitySchemes=self.security_schemas,
        )

    @property
    def server(self):
        return dict(url=self.base_url or self.service.base_url)

    def save(self, file: str):
        schema = self()
        return self.save_to(schema, file)

    @classmethod
    def save_to(cls, schema, file: str, compressed: bool = False):
        if file.endswith(".yaml") or file.endswith(".yml"):
            content = cls.make_yaml(schema)
        else:
            content = json_dumps(schema, indent=None if compressed else 4)

        mode = 'wb' if isinstance(content, bytes) else 'w'
        encoding = "utf-8" if isinstance(content, str) else None

        with open(file, mode=mode, encoding=encoding) as f:
            f.write(content)

        if not os.path.isabs(file):
            file = os.path.join(os.getcwd(), file)
        return file

    @classmethod
    def _resolve_ref(cls, obj, root, visited=None):
        if visited is None:
            visited = set()

        if isinstance(obj, dict):
            if "$ref" in obj:
                ref_path = obj["$ref"]
                if not ref_path.startswith("#/"):
                    raise ValueError(f"暂不支持外部引用: {ref_path}")

                # prevent cycle
                if ref_path in visited:
                    return {"$ref_cycle": ref_path}
                visited.add(ref_path)

                parts = ref_path.lstrip("#/").split("/")
                target = root
                for part in parts:
                    if part not in target:
                        raise KeyError(f"Invalid ref: {ref_path}")
                    target = target[part]

                resolved = cls._resolve_ref(copy.deepcopy(target), root, visited)
                visited.remove(ref_path)
                return resolved
            else:
                return {k: cls._resolve_ref(v, root, visited) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [cls._resolve_ref(i, root, visited) for i in obj]
        else:
            return obj

    @classmethod
    def split_to(cls, openapi: dict, directory: str, format: str = 'json', compressed: bool = False):
        if not isinstance(openapi, OpenAPISchema):
            try:
                openapi = OpenAPISchema(openapi)
            except Exception as e:
                raise e.__class__(f'Invalid openapi schema: {openapi}, raised error: {e}') from e
        os.makedirs(directory, exist_ok=True)

        for path, methods in openapi.paths.items():
            for method, operation in methods.items():
                if not isinstance(operation, dict) or str(method).upper() not in HTTP_METHODS:
                    continue

                operation_id = operation.get("operationId")
                if not operation_id:
                    operation_id = f"{method}_{path.strip('/').replace('/', '_') or 'root'}"

                resolved_operation = cls._resolve_ref(operation, openapi)
                resolved_operation.update(
                    method=method,
                    path=path,
                )

                if format in ('yml', 'yaml'):
                    suffix = 'yml'
                    content = cls.make_yaml(resolved_operation,
                                            key_orders=cls.OPERATION_FIELD_ORDERS)
                else:
                    suffix = 'json'
                    content = json_dumps(resolved_operation, indent=None if compressed else 4)

                file_path = os.path.join(directory, f"{operation_id}.{suffix}")

                mode = 'wb' if isinstance(content, bytes) else 'w'
                encoding = "utf-8" if isinstance(content, str) else None

                with open(file_path, mode=mode, encoding=encoding) as f:
                    f.write(content)

                print(f'writing [{operation_id}] to {file_path}')
        return directory

    @classmethod
    def make_yaml(cls, data: dict, key_orders=tuple(FIELD_ORDERS)):
        requires(yaml="pyyaml>=5.1")
        import yaml  # requires pyyaml
        yaml_kwargs = dict()
        if yaml.__version__ >= '5.1':
            yaml_kwargs.update(sort_keys=False)
        return yaml.dump(
            normalize_dict(data, key_orders=key_orders),
            **yaml_kwargs,
            default_flow_style=False,
            encoding='utf-8',
            allow_unicode=True
        )

    @classmethod
    def as_api(cls, path: str = None, private: bool = True, external_docs=None, json_compressed: bool = False):
        from utilmeta.core import api

        # if path is not specified, use local mem instead
        class OpenAPI_API(API):
            response = Response

            @api.get(private=private)
            def get(self):
                from utilmeta import service

                global _generated_document
                # if _generated_document:
                #     return _generated_document

                # external_docs = None
                # from utilmeta.ops import Operations
                # ops_config = service.get_config(Operations)
                # if ops_config:
                #     external_docs = ops_config.openapi
                openapi = cls(service, external_docs=external_docs)
                # generate document
                if not _generated_document:
                    _generated_document = openapi()

                is_yaml = False
                file_path = ''
                if path:
                    file_path = os.path.join(service.project_dir, path)
                    if path.endswith(".yml") or path.endswith(".yaml"):
                        is_yaml = True
                else:
                    if ".yaml" in self.request.path or ".yml" in self.request.path:
                        is_yaml = True

                if is_yaml:
                    content = cls.make_yaml(_generated_document)
                else:
                    content = json_dumps(_generated_document, indent=None if json_compressed else 4)

                if file_path:
                    with open(file_path, "w") as f:
                        f.write(content)

                return content

        return OpenAPI_API

    @classmethod
    def _path_join(cls, *routes):
        return "/" + "/".join([str(r or "").strip("/") for r in routes]).rstrip("/")

    def generate_info(self) -> OpenAPIInfo:
        data = dict(
            title=self.service.title or self.service.name,
            description=self.service.description or self.service.title or "",
            version=self.service.version_str,
        )
        if self.service.info:
            data.update(self.service.info)
        return OpenAPIInfo(**data)

    def generate_paths(self):
        api = self.service.resolve()
        if not issubclass(api, API):
            raise TypeError(f"Invalid root_api: {api}")
        # return self.from_api(api, path=self.service.root_url)
        return self.from_api(api)

    @classmethod
    def merge_requires(cls, base_requires: List[dict], requires: List[dict]) -> list:
        if not base_requires:
            return requires
        if not requires:
            return base_requires
        base_optional = {} in base_requires
        optional = {} in requires
        res = []
        mp = {}
        for base_req in base_requires:
            if not base_req:
                continue
            mp.update(base_req)

        for req in requires:
            if not req:
                continue
            for k, v in req.items():
                if not mp.get(k) and v:
                    mp[k] = v

        for k, v in mp.items():
            res.append({k: v})
        if base_optional and optional:
            res.append({})
        return res

    def get_response_name(self, response: Type[Response], names: list = ()):
        if response == Response:
            return Response.__name__
        if response in self.responses:
            for k, v in self.response_names.items():
                if v == response:
                    return k
        names = list(names)
        names.append(response.name or get_obj_name(response))
        return re.sub("[^A-Za-z0-9]+", "_", "_".join(names)).strip("_")

    def set_response(self, response: Type[Response], names: list = ()):
        name = self.get_response_name(response, names=names)

        if response in self.responses:
            return name

        gen = self.get_generator(response, output=True)
        data = gen.generate_for_response(response)

        while name in self.response_names:
            resp = self.response_names.get(name)
            resp_data = self.responses.get(resp)
            if resp_data and str(resp_data) == str(data):
                # exact data
                return name
            # de-duplicate name
            name += "_1"

        self.responses[response] = data
        self.response_names[name] = response
        return name

    def parse_properties(
        self, props: Dict[str, ParserProperty]
    ) -> Tuple[list, dict, list]:
        params = []
        media_types = {}
        body_params = {}
        body_form = False
        body_params_required = []
        body_required = None
        body_descriptions = []
        auth_requirements = []

        for key, prop_holder in props.items():
            if not isinstance(prop_holder, ParserProperty):
                continue
            name = prop_holder.name
            field = prop_holder.field
            prop = prop_holder.prop

            auth = None
            scope = []
            if isinstance(prop, User):
                scope = ["login"]
                auth = prop.authentication
                if not prop.required:
                    auth_requirements.append({})
                    # empty object means optional requirement
            elif isinstance(prop, BaseAuthentication):
                # authentication:
                auth = prop

            generator = self.get_generator(field.type)
            field_schema = generator.generate_for_field(field)

            if auth:
                security_name = auth.name
                security_schema = auth.openapi_scheme()
                if security_schema:
                    # todo: oauth2 scopes
                    self.security_schemas[security_name] = security_schema
                    auth_requirements.append({security_name: scope})
                continue

            if prop.__in__:
                # this prop is in the __in__
                if inspect.isclass(prop.__in__) and issubclass(prop.__in__, Property):
                    _in = prop.__in__.__ident__
                else:
                    _in = str(prop.__in__)

                if _in == "body":
                    if field.is_required(generator.options):
                        body_params_required.append(name)
                    body_params[name] = field_schema
                    if field_schema:
                        if field_schema.get("type") == "array":
                            if field_schema.get("items", {}).get("format") == "binary":
                                body_form = True
                        elif field_schema.get("format") == "binary":
                            body_form = True

                elif _in in self.PARAMS_IN:
                    data = {
                        "in": _in,
                        "name": name,
                        "required": field.required,
                        # prop may be injected
                        "schema": field_schema,
                    }
                    if prop.description:
                        data["description"] = prop.description
                    if prop.deprecated:
                        data["deprecated"] = True

                    if isinstance(field.field, properties.RequestParam):
                        if field.field.style:
                            data.update(style=field.field.style)
                    if not unprovided(field.field.example):
                        data.update(example=field.field.example)

                    params.append(data)

            elif prop.__ident__ == "body":
                schema = field_schema
                # treat differently
                content_type = getattr(prop, "content_type", None)
                if not content_type:
                    # guess
                    content_type = generator.get_body_content_type(schema) or PLAIN

                if isinstance(schema, dict) and {'type': 'null'} in (schema.get('anyOf') or []):
                    # Optional[BodySchema]
                    body_required = False
                    body_conditions = list(schema.get('anyOf'))
                    body_conditions.remove({'type': 'null'})
                    if len(body_conditions) == 1:
                        schema = body_conditions[0]

                current_content = media_types.get(content_type)
                body_schema = {"schema": schema}

                if current_content:
                    current_schema = current_content.get('schema')
                    if current_schema:
                        all_of = current_schema.get('allOf')
                        if isinstance(all_of, list):
                            all_of.append(schema)
                            body_schema = {'schema': all_of}
                        else:
                            body_schema = {'schema': {'allOf': [current_schema, schema]}}

                media_types[content_type] = body_schema
                if prop.description:
                    body_descriptions.append(prop.description)

                if len(media_types) > 1:
                    body_required = True
                if body_required is None:
                    body_required = prop.required

            elif prop.__ident__ in self.PARAMS_IN:
                # all the params in this prop is in the __ident__
                # should ex
                schema = field_schema
                prop_schema = generator.get_schema(schema) or {}
                schema_type = prop_schema.get("type")

                if not prop_schema or schema_type != "object":
                    raise TypeError(
                        f"Invalid object type: {field.type} for request property: "
                        f"{repr(prop.__ident__)}, must be a object type, got {repr(schema_type)}"
                    )

                props = prop_schema.get("properties") or {}
                required = prop_schema.get("required") or []
                for prop_name, value in props.items():
                    params.append(
                        {
                            "in": prop.__ident__,
                            "name": prop_name,
                            "schema": value,
                            "required": prop_name in required,
                            # 'style': 'form',
                            # 'explode': True
                        }
                    )

        if media_types:
            if body_params:
                generator = self.get_generator(None)

                for ct in list(media_types):
                    schema: dict = media_types[ct].get("schema")
                    if not schema:
                        continue
                    body_schema = dict(generator.get_schema(schema))
                    body_props = body_schema.get("properties") or {}
                    body_props.update(body_params)
                    body_schema["properties"] = body_props
                    media_types[ct]["schema"] = body_schema

                    if body_form and ct != MULTIPART:
                        media_types[MULTIPART] = media_types.pop(ct)

        elif body_params:
            # content type is default to be json
            content_type = MULTIPART if body_form else JSON
            media_types = {
                content_type: {
                    "schema": {
                        "type": "object",
                        "properties": body_params,
                        "required": body_params_required or False,
                    }
                }
            }

        body = None
        if media_types:
            body = dict(content=media_types, required=body_required)
            if body_descriptions:
                body.update(description='\n'.join(body_descriptions))
        return params, body, auth_requirements

    @property
    def default_status(self):
        return str(self.pref.default_response_status or "default")

    def from_endpoint(
        self,
        endpoint: Endpoint,
        tags: list = (),
        extra_params: list = None,
        extra_body: dict = None,
        response_cls: Type[Response] = None,
        extra_responses: dict = None,
        extra_requires: list = None,
    ) -> dict:
        # https://spec.openapis.org/oas/v3.1.0#operationObject
        operation_names = list(tags) + [endpoint.name]
        operation_id = endpoint.operation_id
        if not operation_id or operation_id in self.operations:
            operation_id = "_".join(operation_names)
            if operation_id in self.operations:
                operation_id = endpoint.ref.replace(".", "_")
        self.operations.add(operation_id)

        # tags -----
        tags = list(tags)
        if endpoint.tags:
            # set by @api.method(tags=[...])
            tags = endpoint.tags
            # for tag in endpoint.tags:
            #     if isinstance(tag, str) and tag not in tags:
            #         tags.append(tag)

        params, body, requires = self.parse_properties(endpoint.wrapper.properties)
        responses = dict(extra_responses or {})

        rt = endpoint.return_type
        response_types = endpoint.response_types
        if not response_types and rt is not None:
            response_types.append((response_cls or Response)[rt])

        for resp in endpoint.response_types:
            resp_name = self.set_response(resp, names=operation_names)
            responses[str(resp.status or self.default_status)] = {
                "$ref": f"#/components/responses/{resp_name}"
            }

        if response_cls and response_cls != Response:
            resp_name = self.set_response(response_cls, names=operation_names)
            responses.setdefault(
                str(response_cls.status or self.default_status),
                {"$ref": f"#/components/responses/{resp_name}"},
            )

        if extra_params:
            # _params = dict(extra_params)
            # _params.update(params)
            params.extend(extra_params)
            # endpoint params can override before hook params
            # the more front params should be exposed
        if extra_body:
            body = body or extra_body

        operation: dict = dict(
            operationId=operation_id,
            tags=self.add_tags(tags),
            responses=dict(sorted(responses.items())),
            security=self.merge_requires(extra_requires, requires),
        )
        if params:
            operation.update(parameters=params)
        if body and endpoint.method in HAS_BODY_METHODS:
            operation.update(requestBody=body)
        if endpoint.idempotent is not None:
            operation.update({"x-idempotent": endpoint.idempotent})
        if endpoint.ref:
            operation.update({"x-ref": endpoint.ref})
        extension = endpoint.openapi_extension
        if extension:
            operation.update(extension)
        return operation

    def add_tags(self, tags: list):
        if not tags:
            return []
        tag_names = []
        for tag in tags:
            if not tag:
                continue
            tag_name = None
            if isinstance(tag, str):
                tag_name = tag
            elif isinstance(tag, dict):
                tag_name = tag.get("name")
            if not tag_name:
                continue
            tag_names.append(tag_name)
            if tag_name not in self.tags:
                self.tags[tag_name] = (
                    tag if isinstance(tag, dict) else {"name": tag_name}
                )
        return tag_names

    def from_route(
        self,
        route: APIRoute,
        *routes: str,
        tags: list = (),
        params: list = None,
        response_cls: Type[Response] = None,
        responses: dict = None,
        requires: list = None,
    ) -> dict:
        # https://spec.openapis.org/oas/v3.1.0#pathItemObject
        new_routes = [*routes, route.route] if route.route else list(routes)
        new_tags = [*tags, route.name] if route.name else list(tags)
        # route_tags = route.get_tags()
        path = self._path_join(*new_routes)

        if self.api_prefix:
            if not path.strip('/').startswith(self.api_prefix.strip('/')):
                return {}

        route_data = {
            k: v
            for k, v in dict(
                summary=route.summary,
                description=route.description,
                deprecated=route.deprecated,
            ).items()
            if v is not None
        }

        extra_body = None
        extra_params = []
        extra_requires = []
        extra_responses = dict(
            responses or {}
        )  # the deeper (close to the api response) is prior
        # before hooks
        for before in route.before_hooks:
            prop_params, body, before_requires = self.parse_properties(
                before.wrapper.properties
            )
            if body and not extra_body:
                extra_body = body
            extra_params.extend(prop_params)
            extra_requires = self.merge_requires(extra_requires, before_requires)

        for after in route.after_hooks:
            for rt in after.response_types:
                resp_name = self.set_response(rt, names=list(tags))
                extra_responses[str(rt.status or self.default_status)] = {
                    "$ref": f"#/components/responses/{resp_name}"
                }

        for error, hook in route.error_hooks.items():
            for rt in hook.response_types:
                resp_name = self.set_response(rt, names=list(tags))
                status = rt.status or getattr(error, "status", None) or "default"
                extra_responses.setdefault(
                    str(status), {"$ref": f"#/components/responses/{resp_name}"}
                )
                # set default. because error hooks is not triggered by default

        path_data = {}
        if route.is_endpoint:
            # generate endpoint data
            endpoint_data = self.from_endpoint(
                route.handler,
                # path_args=route.path_args,
                tags=tags,
                extra_params=extra_params,
                extra_body=extra_body,
                response_cls=response_cls,
                extra_responses=extra_responses,
                extra_requires=extra_requires,
            )
            # inject data in the endpoint, not the route with probably other endpoints
            endpoint_data.update(route_data)
            method_data = {route.method: endpoint_data}

            path_data: dict = self.paths.get(path)
            if path_data:
                path_data.update(method_data)
            else:
                self.paths[path] = path_data = method_data
                if params:
                    path_data.update(parameters=params)
            # responses
        else:
            common_params = list(params or [])
            common_params.extend(extra_params)
            core_data = self.from_api(
                route.handler,
                *new_routes,
                tags=new_tags,
                params=common_params,
                response_cls=response_cls,
                responses=extra_responses,
                requires=requires,
            )
            if core_data:
                core_data.update(route_data)
                # only update the core methods route of the API (if have)

        return path_data

    def from_api(
        self,
        api: Type[API],
        *routes,
        tags: list = (),
        params: list = None,
        response_cls: Type[Response] = None,
        responses: dict = None,
        requires: list = None,
    ) -> Optional[dict]:
        if api.__external__:
            # external APIs will not participate in docs
            return None
        core_data = None
        extra_params = list(params or [])
        prop_params, body, prop_requires = self.parse_properties(api._properties)
        extra_params.extend(prop_params)

        api_response = getattr(api, "response", None)
        if Response.is_cls(api_response) and api_response != Response:
            # set response
            self.set_response(api_response, names=list(tags))

        for api_route in api._routes:
            if api_route.private:
                continue
            route_paths = self.from_route(
                api_route,
                *routes,
                tags=tags,
                params=extra_params,
                response_cls=api_response or response_cls,
                responses=responses,
                requires=self.merge_requires(requires, prop_requires),
            )
            if not api_route.route and api_route.method:
                # core api methods
                core_data = route_paths
                continue
        # props
        return core_data
