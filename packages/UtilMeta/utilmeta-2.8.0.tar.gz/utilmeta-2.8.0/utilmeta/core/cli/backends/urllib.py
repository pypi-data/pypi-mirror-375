from .base import ClientRequestAdaptor
from urllib.request import Request, urlopen
from urllib.error import HTTPError
import urllib


class UrllibRequestAdaptor(ClientRequestAdaptor):
    # @classmethod
    # def reconstruct(cls, adaptor: 'RequestAdaptor'):
    #     return cls(Request(
    #         method=adaptor.method,
    #         url=adaptor.url,
    #         data=adaptor.body,
    #         headers=adaptor.headers
    #     ))
    backend = urllib

    def __call__(self, timeout: float = None, **kwargs):
        from utilmeta.core.response.backends.urllib import UrllibResponseAdaptor

        try:
            resp = urlopen(
                Request(
                    url=self.request.url,
                    method=str(self.request.method).upper(),
                    data=self.request.body,
                    headers=self.request.headers,
                ),
                timeout=float(timeout) if timeout is not None else None,
            )
        except HTTPError as e:
            resp = e
        return UrllibResponseAdaptor(resp)
