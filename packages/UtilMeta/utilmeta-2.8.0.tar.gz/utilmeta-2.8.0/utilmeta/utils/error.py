import traceback
from typing import Type, Dict, Callable, Optional, List, TYPE_CHECKING
from . import Attr, SEG, readable
import sys
import inspect
import time

if TYPE_CHECKING:
    from utilmeta.core.request.base import Request

CAUSE_DIVIDER = (
    "\n# The above exception was the direct cause of the following exception:\n"
)


class Error:
    MAX_CAUSE_DEPTH: int = 3

    def __init__(self, e: Exception = None, request: "Request" = None):
        if isinstance(e, Exception):
            self.exc = e
            self.type = e.__class__
            self.exc_traceback = e.__traceback__
        elif isinstance(e, Error):
            self.exc = e.exc
            self.type = e.type
            self.exc_traceback = e.exc_traceback
        else:
            exc_type, exc_instance, exc_traceback = sys.exc_info()
            self.exc = exc_instance
            self.type = exc_type
            self.exc_traceback = exc_traceback

        self.locals = {}
        self.current_traceback = ""
        self.traceback = ""
        self.variable_info = ""
        self.full_info = ""
        self.ts = time.time()

        # request context
        self.request = request

    def setup(
        self,
        from_errors: list = (),
        with_cause: bool = True,
        with_variables: bool = True,
        depth: int = 0
    ):
        if self.current_traceback:
            return
        # FIXME: lots of performance cost in this function
        self.current_traceback = "".join(traceback.format_tb(self.exc_traceback))
        self.traceback = self.current_traceback
        if not from_errors and with_variables:
            try:
                self.locals = inspect.trace()[-1][0].f_locals
                # self.locals: Dict[str, Any] = Util.clean_kwargs(inspect.trace()[-1][0].f_locals, display=True)
            except IndexError:
                self.locals = {}

        if with_cause and depth < self.MAX_CAUSE_DEPTH:
            # fixme:
            cause = self.exc.__cause__
            from_errors = [self.exc] + list(from_errors)

            if cause and cause not in from_errors:
                cause_error = self.__class__(cause)
                cause_error.setup(
                    from_errors=from_errors,
                    with_variables=with_variables,
                    with_cause=with_cause,
                    depth=depth + 1
                )
                self.traceback = cause_error.full_info + CAUSE_DIVIDER + self.traceback
                # self.locals.update({
                #     f'{cause.__class__.__name__}.{key}': val for key, val in cause_error.locals.items()
                # })

        from utilmeta.conf import Preference
        pref = Preference.get()
        variables = []
        if self.locals:
            variables.append("Exception Local Variables:")
        for key, val in self.locals.items():
            if key.startswith(SEG) and key.endswith(SEG):
                continue
            try:
                variables.append(f"{key} = {readable(val, max_length=pref.error_variable_max_length)}")
            except Exception as e:
                print(f"Variable <{key}> serialize error: {e}")
        self.variable_info = "\n".join(variables)
        self.full_info = "\n".join([self.message, *variables])

    def __str__(self):
        return f"<{self.type.__name__}: {str(self.exc)}>"

    @property
    def exception(self):
        return self.exc

    @property
    def message(self) -> str:
        return "{0}{1}: {2}".format(self.traceback, self.type.__name__, self.exc)

    @property
    def status(self) -> int:
        return self.get_status(default=500)

    def get_status(self, default=None):
        status = getattr(self.exc, "status", None)
        if isinstance(status, int) and 100 <= status <= 600:
            return status
        return default

    @property
    def result(self):
        return getattr(self.exc, "result", None)

    @property
    def state(self):
        return getattr(self.exc, "state", None)

    @property
    def headers(self):
        return getattr(self.exc, "headers", None)

    def log(self, console: bool = False, with_variables: bool = True) -> int:
        if not self.full_info:
            self.setup(with_variables=with_variables)
        if console:
            print(self.full_info)
        return self.status

    @property
    def cause_func(self):
        stk = traceback.extract_tb(self.exc_traceback, 1)
        return stk[0][2]

    def throw(self, type=None, prepend: str = "", **kwargs):
        if not (inspect.isclass(type) and issubclass(type, Exception)):
            type = None
        type = type or self.type
        if prepend or not isinstance(self.exc, type):
            e = type(f"{prepend}{self.exc}", **kwargs)  # noqa
            e.__cause__ = self.exc
            # setattr(e, Attr.CAUSES, self.get_causes())
        else:
            e = self.exc
        # it need the throw caller to raise the error like: raise Error().throw()
        # cause in that way can track the original variables
        return e

    def get_hook(
        self, hooks: Dict[Type[Exception], Callable], exact: bool = False
    ) -> Optional[Callable]:
        if not hooks:
            return None

        def _get(_e):
            for et, func in hooks.items():
                if et is Exception:
                    continue
                if exact:
                    if _e == et:
                        return func
                else:
                    if isinstance(_e, et):
                        return func

        hook = _get(self.exc)
        if hook or exact:
            return hook

        # exact does not take Exception as the finally fallback
        default = hooks.get(Exception)
        # if self.combined:
        #     values = set()
        #     for err in self:
        #         _hook = _get(err)
        #         if _hook:
        #             values.add(_hook)
        #     if len(values) == 1:
        #         return values.pop()

        return default
