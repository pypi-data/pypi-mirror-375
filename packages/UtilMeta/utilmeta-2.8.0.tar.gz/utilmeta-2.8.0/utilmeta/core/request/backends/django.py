from .base import RequestAdaptor
from django.http.request import HttpRequest
from django.middleware.csrf import CsrfViewMiddleware, get_token
from utilmeta.utils import (
    parse_query_dict,
    Header,
    LOCAL_IP,
    multi,
    url_join,
)
from ipaddress import ip_address
from utilmeta.core.file.backends.django import DjangoFileAdaptor
from utilmeta.core.file.base import File
import django


def get_request_ip(meta: dict):
    ips = [
        *meta.get(Header.FORWARDED_FOR, "").replace(" ", "").split(","),
        meta.get(Header.REMOTE_ADDR),
    ]
    if "" in ips:
        ips.remove("")
    if LOCAL_IP in ips:
        ips.remove(LOCAL_IP)
    for ip in ips:
        try:
            return ip_address(ip)
        except ValueError:
            continue
    return ip_address(LOCAL_IP)


class DjangoRequestAdaptor(RequestAdaptor):
    file_adaptor_cls = DjangoFileAdaptor
    backend = django

    def gen_csrf_token(self):
        return get_token(self.request)

    def check_csrf_token(self) -> bool:
        err_resp = CsrfViewMiddleware(lambda *_: None).process_view(
            self.request, None, None, None
        )
        return err_resp is None

    @property
    def request_method(self):
        return self.request.method

    @property
    def url(self):
        return self._url

    @property
    def address(self):
        return self._address

    def get_url(self):
        if hasattr(self.request, "get_raw_uri"):
            return self.request.get_raw_uri()
        try:
            return self.request.build_absolute_uri()
        except KeyError:
            from utilmeta import service

            return url_join(service.origin, self.path)

    @property
    def path(self):
        return self.request.path

    @classmethod
    def load_form_data(cls, request):
        m = request.method
        load_call = getattr(request, "_load_post_and_files")
        if m in ("PUT", "PATCH"):
            if hasattr(request, "_post"):
                delattr(request, "_post")
                delattr(request, "_files")
            try:
                request.method = "POST"
                load_call()
                request.method = m
            except AttributeError:
                request.META["REQUEST_METHOD"] = "POST"
                load_call()
                request.META["REQUEST_METHOD"] = m

    def get_form(self):
        self.load_form_data(self.request)
        data = parse_query_dict(self.request.POST)
        parsed_files = {}
        for key in self.request.FILES:
            files = self.request.FILES.getlist(key)
            if multi(files):
                parsed_files[key] = [
                    File(self.file_adaptor_cls(file)) for file in files
                ]
            else:
                parsed_files[key] = File(self.file_adaptor_cls(files))
        data.update(parsed_files)
        return data

    # async def async_load(self):
    #     try:
    #         return self.get_content()
    #     except NotImplementedError:
    #         raise
    #     except Exception as e:
    #         raise exceptions.UnprocessableEntity(f'process request body failed with error: {e}') from e

    async def async_read(self):
        # from django.core.handlers.asgi import ASGIRequest
        # if isinstance(self.request, ASGIRequest):
        #     return self.request.read()
        return self.body
        # not actually "async", but could be used from async server

    # @cached_property
    # def encoded_path(self):
    #     try:
    #         return self.request.get_full_path()
    #     except AttributeError:
    #         from django.utils.encoding import escape_uri_path
    #         # RFC 3986 requires query string arguments to be in the ASCII range.
    #         # Rather than crash if this doesn't happen, we encode defensively.
    #         path = escape_uri_path(self.request.path)
    #         qs = self.request.META.get('QUERY_STRING', '')
    #         if qs:
    #             path += '?' + qs
    #         return path

    @property
    def body(self):
        return self.request.body

    @property
    def headers(self):
        return self._headers

    @property
    def scheme(self):
        return self.request.scheme

    # @property
    # def query_string(self):
    #     return self.request.META.get('QUERY_STRING', '')

    @property
    def query_params(self):
        return parse_query_dict(self.request.GET)

    @property
    def cookies(self):
        return self.request.COOKIES

    def __init__(self, request: HttpRequest, route: str = None, *args, **kwargs):
        super().__init__(request, route, *args, **kwargs)
        # django request.META might lost if the current request context is finished
        # so we need to save it to the local vars
        self._headers = self.request.headers
        self._address = get_request_ip(self.request.META)
        self._url = self.get_url()
