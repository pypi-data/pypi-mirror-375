from http.client import HTTPResponse
from urllib.error import HTTPError
from typing import Union
from .base import ResponseAdaptor
from utilmeta.utils import Headers


class UrllibResponseAdaptor(ResponseAdaptor):
    response: Union[HTTPResponse, HTTPError]

    def iter_bytes(self, chunk_size=None):
        chunk_size = chunk_size or self.get_default_chunk_size() or 1024
        while True:
            chunk = self.response.read(chunk_size)
            if not chunk:
                break
            yield chunk

    @classmethod
    def qualify(cls, obj):
        return isinstance(obj, (HTTPResponse, HTTPError))

    @property
    def status(self):
        return self.response.status

    @property
    def reason(self):
        return self.response.reason

    @property
    def url(self):
        return str(self.response.url)

    @property
    def headers(self):
        return Headers(dict(self.response.headers))

    @property
    def body(self):
        if self._body is not None:
            return self._body
        self._body = self.response.read()
        return self._body

    @property
    def cookies(self):
        from http.cookies import SimpleCookie

        cookies = SimpleCookie()
        for cookie in self.response.headers.get_all("Set-Cookie") or []:
            # use get_all, cause Set-Cookie can be multiple
            cookies.load(cookie)
        return cookies

    def close(self):
        self.response.close()
