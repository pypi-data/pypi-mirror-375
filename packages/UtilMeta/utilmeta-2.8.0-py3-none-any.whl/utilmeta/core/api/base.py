from typing import Union, Dict, Type, List, Any, Optional
from utilmeta.utils.error import Error
from utilmeta.utils.context import ParserProperty
from utilmeta.utils import (
    Header,
    EndpointAttr,
    COMMON_METHODS,
    awaitable,
    classonlymethod,
    distinct_add,
)
from utilmeta.utils import exceptions as exc

import inspect
import warnings

from functools import partial
from utilmeta.utils import PluginEvent, PluginTarget, Property
from utype.parser.field import ParserField
from utype import Options
from utype.utils.datastructures import unprovided
from ..response import Response
from ..request import Request, var
from .route import APIRoute
from .endpoint import Endpoint
from .hook import Hook, ErrorHook, BeforeHook, AfterHook
from .chain import APIChainBuilder
from . import decorator
from utype.utils.compat import is_annotated
from utype.utils.exceptions import ParseError
from utilmeta.conf import Preference

setup_class = PluginEvent("setup_class", synchronous_only=True)
# enter_route = PluginEvent('enter_route')
# exit_route = PluginEvent('exit_route')
setup_instance = PluginEvent("setup_instance")


class APIRef:
    def __init__(self, ref_string: str):
        self.ref = ref_string
        self._api = None

    @property
    def api(self) -> Type["API"]:
        if self._api:
            return self._api
        from utilmeta.utils import import_obj

        api = import_obj(self.ref)
        if not issubclass(api, API):
            raise TypeError(
                f"Invalid ref: {repr(self.ref)}, should be an API class, got {api}"
            )
        self._api = api
        return api


class API(PluginTarget):
    __options__ = Options()
    # flags
    __external__ = False
    # ---

    _generator: decorator.APIGenerator
    _routes: List[APIRoute]
    _properties: Dict[str, ParserProperty]
    _annotations: Dict[str, type]
    _hook_cls: Type[Hook] = Hook
    _error_cls: Type[Error] = Error
    _route_cls: Type[APIRoute] = APIRoute
    _endpoint_cls: Type[Endpoint] = Endpoint
    _chain_cls: Type[APIChainBuilder] = APIChainBuilder
    _parser_field_cls: Type[ParserField] = ParserField
    _default_error_hooks: Dict[Type[Exception], ErrorHook]
    _request_cls: Type[Request]
    _response_cls: Optional[Type[Response]] = None

    request: Request
    response: Type[Response]

    @classonlymethod
    def _parse_bases(cls):
        base_routes = []
        error_hooks = {}
        properties = {}  # take all base's properties as well
        base_properties = {}
        annotations = {}

        for base in reversed(cls.__bases__):  # mro
            if issubclass(base, API) and base.__bases__ != (object,):
                annotations.update(getattr(base, "_annotations", {}))
                base_routes.extend(getattr(base, "_routes", []))
                error_hooks.update(getattr(base, "_default_error_hooks", {}))
                properties.update(getattr(base, "_properties", {}))
            else:
                # if base have no annotations, there won't be any __annotations__ attribute
                annotations.update(getattr(base, "__annotations__", {}))
                # other common class mixin with no bases, check the properties
                for key, val in base.__dict__.items():
                    if inspect.isclass(val) and issubclass(val, Property):
                        val = val()
                    if isinstance(val, Property):
                        base_properties[key] = val

        annotations.update(cls.__annotations__)
        cls._annotations = annotations
        cls._properties = properties

        for key, val in base_properties.items():
            if key in annotations:
                cls._make_property(key, val)

        cls._routes = base_routes
        cls._default_error_hooks = error_hooks
        if Response.is_cls(getattr(cls, "response", None)):
            cls._response_cls = cls.response
        else:
            cls._response_cls = None

    @classonlymethod
    def _check_unit_name(cls, name: str):
        if name in COMMON_METHODS:
            return
        for base in cls.__bases__:
            base_attr = getattr(base, name, None)
            if base_attr is None:
                continue
            if isinstance(base_attr, Endpoint):
                # override base class's unit (or hook)
                continue
            raise AttributeError(
                f"{cls} function <{name}> is already a baseclass ({base}) attribute or method, "
                f"cannot make it a hook or api function, please change it to another name"
            )

    def __init_subclass__(cls, **kwargs):
        cls.__annotations__ = cls.__dict__.get("__annotations__", {})
        cls._parse_bases()
        cls._generate_routes()
        cls._validate_routes()
        cls._request_cls: Type[Request] = cls._annotations.get("request") or Request
        if not issubclass(cls._request_cls, Request):
            raise TypeError(
                f"Invalid request class: {cls._request_cls}, must be subclass of Request"
            )
        req = getattr(cls, "request", None)
        if req is not None:
            if not isinstance(req, Request):
                raise TypeError(
                    f'Invalid "request" attribute: {req}, {cls} should use other attr names'
                )
            cls._request_cls = req.__class__
        resp = getattr(cls, "response", None)
        if resp is not None:
            if not issubclass(resp, Response):
                raise TypeError(
                    f'Invalid "response" attribute: {resp}, {cls} should use other attr names'
                )

        setup_class(cls, **kwargs)
        super().__init_subclass__(**kwargs)

    @classonlymethod
    def _generate_routes(cls):
        routes = []
        hooks = []
        handlers = []
        default_error_hooks = {}

        # COLLECT ANNOTATIONS FORM
        for key, api in cls.__annotations__.items():
            if key.startswith("_"):
                continue
            val = cls.__dict__.get(key)

            if isinstance(api, APIRef):
                api = api.api

            elif is_annotated(api):
                # param: Annotated[str, request.QueryParam()]
                for m in getattr(api, "__metadata__", []):
                    if inspect.isclass(m) and issubclass(m, Property):
                        m = m()
                    if isinstance(m, Property):
                        cls._make_property(key, m)
                        break
                api = getattr(api, "__origin__", None)

            if inspect.isclass(api) and issubclass(api, API):
                kwargs = dict(route=key, name=key, parent=cls)
                if not val:
                    val = getattr(api, "_generator", None)
                if isinstance(val, decorator.APIGenerator):
                    kwargs.update(val.kwargs)
                elif inspect.isfunction(val):
                    raise TypeError(
                        f"{cls.__name__}: generate route [{repr(key)}] failed: conflict api and endpoint"
                    )
                handlers.append(api)
                try:
                    route = cls._route_cls(api, **kwargs)
                except Exception as e:
                    raise e.__class__(
                        f"{cls.__name__}: generate route [{repr(key)}] failed with error: {e}"
                    ) from e
                if route.private:
                    continue
                # route.initialize(cls)
                routes.append(route)
                # make the annotated key as a property that can access through instance
                setattr(cls, key, route.make_property())

            # ---------------------------------------------------
            if inspect.isclass(val) and issubclass(val, Property):
                # eg: logger: Logger
                if key not in cls.__dict__:
                    context = getattr(val, "__context__", None)
                    if context and isinstance(context, Property):
                        cls._make_property(key, context)

        local_vars = {k: v for k, v in cls.__dict__.items() if not k.startswith("_")}

        for key, val in cls.__dict__.items():
            if val in handlers:
                # already been added
                continue
            if isinstance(val, APIRef):
                val = val.api

            if inspect.isclass(val) and issubclass(val, API):
                kwargs = dict(route=key, name=key, parent=cls)
                generator = getattr(val, "_generator", None)
                if isinstance(generator, decorator.APIGenerator):
                    kwargs.update(generator.kwargs)
                handlers.append(val)
                try:
                    route = cls._route_cls(val, **kwargs)
                except Exception as e:
                    raise e.__class__(
                        f"{cls.__name__}: generate route [{repr(key)}] failed with error: {e}"
                    ) from e
                if route.private:
                    continue
                # route.initialize(cls)
                routes.append(route)
                continue

            if inspect.isfunction(val):
                if key.lower() in COMMON_METHODS:
                    val.method = key.lower()

                method = getattr(val, EndpointAttr.method, None)
                hook_type = getattr(val, EndpointAttr.hook, None)

                if method:
                    # a sign to wrap it in Unit
                    # 1. @api.get                (method='get')
                    # 2. @api.parser             (method=None)
                    # 3. def get(self):          (method='get')
                    # 4. @api(method='CUSTOM')   (method='custom')
                    try:
                        val = cls._endpoint_cls.apply_for(
                            val, cls, name=key, local_vars=local_vars
                        )
                    except Exception as e:
                        raise e.__class__(
                            f"{cls.__name__}: "
                            f"generate endpoint [{repr(key)}] failed with error: {e}"
                        ) from e
                elif hook_type:
                    val = cls._hook_cls.dispatch_for(val, hook_type)
                else:
                    continue

                setattr(cls, key, val)  # reset value

            if isinstance(val, Endpoint):
                # val: Endpoint
                cls._check_unit_name(key)
                handlers.append(val)
                if val.method:
                    try:
                        route = cls._route_cls(
                            val,
                            name=key,
                            route=val.route,
                            summary=val.getattr("summary"),
                            tags=val.getattr("tags"),
                            description=val.getattr("description"),
                            deprecated=val.getattr("deprecated"),
                            private=val.getattr("private"),
                            priority=val.getattr("priority"),
                        )
                    except Exception as e:
                        raise e.__class__(
                            f"{cls.__name__}: generate route [{repr(key)}] failed with error: {e}"
                        ) from e
                    routes.append(route)
                continue

            if isinstance(val, Hook):
                hooks.append(val)
                if isinstance(val, ErrorHook) and val.hook_all:
                    for err in val.hook_errors:
                        default_error_hooks[err] = val
                continue

            if inspect.isclass(val) and issubclass(val, Property):
                val = val()

            if isinstance(val, Property) and key in cls._annotations:
                # only key: <type> = <prop> in class is consider a valid api property
                cls._make_property(key, val)

        for hook in hooks:
            if not any([route.hook(hook) for route in routes]):
                # hook the function for every endpoint
                # .hook() return a bool to indicate whether hooked
                # if not any() hooked, the target expression of the hook maybe invalid
                # we will give it a warning
                if not hook.hook_all:
                    msg = f"{cls}: unmatched hook: {hook} with targets: {hook.hook_targets}"
                    warnings.warn(msg)
                    # from utilmeta.conf import config
                    # if config.preference.ignore_unmatched_hooks:
                    #     warnings.warn(msg)
                    # else:
                    # raise ValueError(msg)

        # compile route after mount hooks
        for route in routes:
            try:
                route.compile_route()
            except Exception as e:
                raise e.__class__(f'{cls}: compile route [{route.name}] '
                                  f'failed with error: {e}') from e

        cls._routes.extend(routes)
        cls._default_error_hooks.update(default_error_hooks)

    @classmethod
    def _get_route_pattern(cls):
        patterns = []
        for route in cls._routes:
            patterns.extend(route.get_patterns())
        if not patterns:
            return ""
        return "^(%s)$" % "|".join(patterns)

    @classonlymethod
    def _global_vars(cls):
        import sys

        return sys.modules[cls.__module__].__dict__

    @classonlymethod
    def _make_property(cls, name: str, prop: Property):
        _in = getattr(prop.__in__, "__ident__", None)
        if prop.__ident__ == "body" or _in == "body":
            raise ValueError(
                f"{cls.__name__}: API class cannot define "
                f"Body or BodyParam common params: [{repr(name)}]"
            )

        field = cls._parser_field_cls.generate(
            attname=name,
            default=prop,
            annotation=cls._annotations.get(name),
            options=cls.__options__,
            global_vars=cls._global_vars(),
        )

        inst = prop.init(field)

        def getter(self: "API"):
            if name in self.__dict__:
                return self.__dict__[name]
            value = inst.get(self.request)
            if unprovided(value):
                default = field.get_default(cls.__options__, defer=None)
                if not unprovided(default):
                    # NOT CACHE
                    return default
                raise exc.BadRequest(
                    f"{cls.__name__}: "
                    f"{prop.__class__.__name__}({repr(field.name)}) not provided"
                )
            try:
                value = field.parse_value(
                    value, context=self.__options__.make_context(cls)
                )
            except ParseError as e:
                raise exc.BadRequest(str(e), detail=e.get_detail()) from e
            self.__dict__[name] = value  # auto-cached
            return value

        getter.__field__ = prop

        setter = None
        if prop.setter != Property.setter:

            def setter(self: "API", value):
                inst.set(self.request, value)
                self.__dict__[name] = value  # auto-cached

        setattr(cls, name, property(getter, setter))
        cls._properties[name] = inst

    @classonlymethod
    def _validate_routes(cls):
        route_idents = {}
        api_routes = {}

        for api_route in cls._routes:
            if api_route.ident in route_idents:
                raise ValueError(
                    f"{cls}: api {api_route.handler} conflict with "
                    f"{route_idents[api_route.ident]} on identity: {repr(api_route.ident)}"
                )
            route_idents[api_route.ident] = api_route.handler
            if not api_route.method:
                api_routes[api_route.route] = api_route.handler

        for api_route in cls._routes:
            if api_route.method:
                if api_route.route in api_routes:
                    raise ValueError(
                        f"{cls}: api function: {api_route.handler} "
                        f"route: {repr(api_route.route)} conflict "
                        f"with api class: {api_routes[api_route.route]}"
                    )
        # TODO: test if any static route is override by a higher priority dynamic route

    @classonlymethod
    def __reproduce_with__(cls, generator: decorator.APIGenerator):
        plugins = generator.kwargs.get("plugins")
        if plugins:
            cls._add_plugins(*plugins)
        cls._generator = generator
        return cls

    # @classonlymethod
    @classmethod
    def __as__(cls, backend, route: str, *, asynchronous: bool = None):
        from utilmeta import UtilMeta
        if isinstance(backend, UtilMeta):
            service = backend
        else:
            try:
                from utilmeta import service
            except ImportError:
                service = UtilMeta(
                    None, backend=backend, name=route.strip("/").replace("/", "_")
                )
                service._auto_created = True
            service.mount_to_api(cls, route=route)
        # backend can be a module name or application
        adaptor = service.adaptor
        return adaptor.adapt(cls, route=route, asynchronous=asynchronous)

    @classonlymethod
    def __mount__(
        cls,
        handler: Union[APIRoute, Type["API"], APIRef, Endpoint, str],
        route: str = "",
        before_hooks: List[BeforeHook] = (),
        after_hooks: List[AfterHook] = (),
        error_hooks: Dict[Type[Exception], ErrorHook] = None,
    ):
        if isinstance(handler, APIRef):
            handler = handler.api
        if isinstance(handler, str):
            from utilmeta.utils import import_obj

            handler = import_obj(handler)
        if isinstance(handler, APIRoute):
            cls._routes.append(handler)
            return
        if any([r.handler == handler and r.route == route for r in cls._routes]):
            # same route and handler, return
            return

        api_route = cls._route_cls(
            handler=handler,
            route=route,
            name=route.replace("/", "_"),
            before_hooks=before_hooks,
            after_hooks=after_hooks,
            error_hooks=error_hooks,
        )
        api_route.compile_route()
        cls._routes.append(api_route)
        cls._validate_routes()  # validate each time there is a new api mount

    def __init__(self, request):
        super().__init__()
        self.request = self._request_cls.apply_for(request)
        self.response = getattr(self, "response", Response)
        # set request before setup instance, cause this hook may depend on the request context
        for key, val in self.__class__.__dict__.items():
            if isinstance(val, Endpoint):
                setattr(self, key, partial(val, self))
            if isinstance(val, Hook):
                setattr(self, key, partial(val, self))

        self._response_types = []
        self._error_hooks = self._default_error_hooks
        self._init_properties()
        setup_instance(self)

    def _init_properties(self):
        if not self._properties:
            return
        context = self.__options__.make_context(cls=__class__)
        for name, prop in self._properties.items():
            value = prop.get(self.request)
            if not unprovided(value):
                try:
                    value = prop.field.parse_value(value, context=context)
                except ParseError as e:
                    if self.request.is_options:
                        # ignore parse error for OPTIONS request
                        continue
                    raise exc.BadRequest(str(e), detail=e.get_detail()) from e
                self.__dict__[name] = value

    def _resolve(self) -> APIRoute:
        method_routes: Dict[str, APIRoute] = {}
        for route in self._routes:
            if route.match_route(self.request):
                # path math
                if not route.method:
                    # not endpoint
                    # further API mount
                    return route
                else:
                    # elif route.method == self.request.method and not self.request.is_options:
                    #     # options/cross-origin need to collect methods to generate Allow-Methods
                    #     return route
                    # first match is 1st priority
                    method_routes.setdefault(route.method, route)

        if method_routes:
            allow_methods = var.allow_methods.setup(self.request)
            allow_headers = var.allow_headers.setup(self.request)
            route_var = var.unmatched_route.setup(self.request)
            allow_methods.set(list(method_routes))
            headers = list(allow_headers.get() or [])
            for route in method_routes.values():
                distinct_add(headers, route.header_names)
            allow_headers.set(headers)
            route_var.set("")
            if self.request.method not in method_routes:
                raise exc.MethodNotAllowed(
                    method=self.request.method, allows=allow_methods.get()
                )
            return method_routes[self.request.method]
        raise exc.NotFound(path=self.request.path)

    def _handle_error(self, error: Error):
        hook = error.get_hook(
            self._error_hooks, exact=isinstance(error.exception, exc.Redirect)
        )
        # hook applied before handel_error plugin event
        if hook:
            result = hook(self, error)
            if not isinstance(result, Error):
                return result
            error = result
        raise error.throw()

    async def _async_handle_error(self, error: Error):
        hook = error.get_hook(
            self._error_hooks, exact=isinstance(error.exception, exc.Redirect)
        )
        # hook applied before handel_error plugin event
        if hook:
            result = hook(self, error)
            if inspect.isawaitable(result):
                result = await result
            if not isinstance(result, Error):
                return result
            error = result
        raise error.throw()

    def _make_response(self, response, force: bool = False):
        if isinstance(response, Response):
            if not response.request:
                response.request = self.request
            return response
        request = self.request
        pref = Preference.get()
        for i, resp_type in enumerate(self._response_types):
            try:
                return resp_type(
                    response, request=request, strict=pref.api_default_strict_response
                )
            except Exception as e:
                if (
                    i == len(self._response_types) - 1
                    and pref.api_default_strict_response
                ):
                    raise e from e
                continue
        if self._response_cls:
            return self._response_cls(
                response, request=request, strict=pref.api_default_strict_response
            )
        if force:
            return Response(response, request=request)
        return response

    def __handler__(self):
        # resolve after process request for API
        # because process request may change request path / method
        with self._resolve() as route:
            self._error_hooks = route.error_hooks
            return route.serve(self)

    async def __async_handler__(self):
        with self._resolve() as route:
            self._error_hooks = route.error_hooks
            return await route.aserve(self)

    def __call__(self) -> Union[Response, Any]:
        handler = self._chain_cls(self).build_api_handler(
            self.__class__.__handler__, asynchronous=False
        )
        try:
            resp = handler(self)
        except Exception as e:
            resp = self._handle_error(Error(e, request=self.request))
        return self._make_response(resp)

    @awaitable(__call__)
    async def __call__(self) -> Union[Response, Any]:
        handler = self._chain_cls(self).build_api_handler(
            self.__class__.__async_handler__, asynchronous=True
        )
        try:
            resp = await handler(self)
        except Exception as e:
            resp = await self._async_handle_error(Error(e, request=self.request))
        return self._make_response(resp)

    def options(self):
        return Response(
            headers={
                Header.ALLOW: ",".join(
                    set([m.upper() for m in var.allow_methods.getter(self.request)])
                ),
                Header.LENGTH: "0",
            }
        )

    def __serve__(self, unit):
        if isinstance(unit, Endpoint):
            handler = self._chain_cls(self, unit).build_api_handler(
                unit.handler, asynchronous=False
            )
            var.endpoint_ref.setter(self.request, unit.ref)
            self._response_types = unit.response_types
            return handler(self)
        else:
            return unit(self.request)()

    async def __aserve__(self, unit):
        if isinstance(unit, Endpoint):
            handler = self._chain_cls(self, unit).build_api_handler(
                unit.async_handler, asynchronous=True
            )
            var.endpoint_ref.setter(self.request, unit.ref)
            self._response_types = unit.response_types
            return await handler(self)
        else:
            return await unit(self.request)()


setup_class.register(API)
setup_instance.register(API)
