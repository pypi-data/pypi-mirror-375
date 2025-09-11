import warnings

from utilmeta.core.response import Response
from utilmeta.core.request import var, Request
from utilmeta.utils.context import ContextProperty, Property
from typing import List, Optional, Union
from utilmeta.core.server import ServiceMiddleware
from utilmeta.utils import (
    HAS_BODY_METHODS,
    hide_secret_values,
    normalize,
    time_now,
    Error,
    ignore_errors,
    replace_null,
    parse_user_agents,
    HTTP_METHODS_LOWER,
)
from .config import Operations
import threading
import contextvars
import time
from functools import wraps
from django.db import models


_responses_queue: List[Response] = []
_endpoints_map: dict = {}
_endpoints_patterns: dict = {}
_worker = None
_server = None
_version = None
_supervisor = None
_instance = None
_databases: dict = {}
_caches: dict = {}
_openapi = None
_path_prefix = ""
_logger = contextvars.ContextVar("_logger")


class WorkerMetricsLogger:
    def __init__(self):
        # common metrics
        self._total_in = 0
        self._total_out = 0
        self._total_outbound_requests = 0
        self._total_outbound_request_time = 0
        self._total_outbound_errors = 0
        self._total_outbound_timeouts = 0

        # request metrics
        self._total_requests = 0
        self._total_errors = 0
        self._total_time = 0

    @ignore_errors
    def log(
        self,
        duration: float,
        in_traffic: int = 0,
        out_traffic: int = 0,
        outbound: bool = False,
        error: bool = False,
        timeout: bool = False,
    ):
        self._total_in += in_traffic
        self._total_out += out_traffic

        if outbound:
            self._total_outbound_requests += 1
            self._total_outbound_errors += 1 if error else 0
            self._total_outbound_timeouts += 1 if timeout else 0
            self._total_outbound_request_time += duration
        else:
            self._total_requests += 1
            self._total_errors += 1 if error else 0
            self._total_time += duration

    def reset(self):
        self._total_requests = 0
        self._total_errors = 0
        self._total_time = 0
        self._total_in = 0
        self._total_out = 0
        self._total_outbound_requests = 0
        self._total_outbound_request_time = 0
        self._total_outbound_errors = 0
        self._total_outbound_timeouts = 0

    def fetch(self, interval: int):
        if not self._total_requests:
            return dict()
        return dict(
            requests=self._total_requests,
            in_traffic=self._total_in,
            out_traffic=self._total_out,
            avg_time=self._total_time / self._total_requests,
            rps=self._total_requests / interval,
            errors=self._total_errors,
            outbound_requests=self._total_outbound_requests,
            outbound_avg_time=(
                self._total_outbound_request_time / self._total_outbound_requests
            )
            if self._total_outbound_requests
            else 0,
            outbound_rps=self._total_outbound_requests / interval,
            outbound_errors=self._total_outbound_errors,
            outbound_timeouts=self._total_outbound_timeouts,
        )

    @ignore_errors(default=dict)  # ignore cache errors
    def retrieve(self, inst) -> dict:
        if not inst:
            return {}

        now = time_now()
        requests = self._total_requests
        in_traffic = self._total_in
        out_traffic = self._total_out
        total_time = self._total_time
        errors = self._total_errors
        outbound_requests = self._total_outbound_requests
        total_outbound_request_time = self._total_outbound_request_time
        outbound_errors = self._total_outbound_errors
        outbound_timeouts = self._total_outbound_timeouts

        values = dict(
            time=now,
        )
        if requests:
            values.update(
                requests=models.F("requests") + requests,
                rps=round(requests / (now - inst.time).total_seconds(), 4),
                avg_time=(
                    (models.F("avg_time") * models.F("requests") + total_time)
                    / (models.F("requests") + requests)
                )
                if requests
                else models.F("avg_time"),
                errors=models.F("errors") + errors,
            )
        if in_traffic:
            values.update(in_traffic=models.F("in_traffic") + in_traffic)
        if out_traffic:
            values.update(out_traffic=models.F("out_traffic") + out_traffic)
        if outbound_requests:
            values.update(
                outbound_requests=models.F("outbound_requests") + outbound_requests,
                outbound_errors=models.F("outbound_errors") + outbound_errors,
                outbound_timeouts=models.F("outbound_timeouts") + outbound_timeouts,
                outbound_rps=round(
                    outbound_requests / (now - inst.time).total_seconds(), 4
                ),
                outbound_avg_time=(
                    (
                        models.F("outbound_requests") * models.F("outbound_avg_time")
                        + total_outbound_request_time
                    )
                    / (models.F("outbound_requests") + outbound_requests)
                )
                if outbound_requests
                else models.F("outbound_avg_time"),
            )

        return replace_null(values)

    def save(self, inst, **kwargs):
        values = self.retrieve(inst)
        kwargs.update(values)
        self.reset()
        models.QuerySet(model=inst.__class__).filter(pk=inst.pk).update(**kwargs)
        return values

    def update_worker(self, record: bool = False, interval: int = None):
        if not _worker:
            return
        from .models import Worker

        worker: Worker = _worker  # noqa
        now = time_now()
        sys_metrics = worker.get_sys_metrics()
        req_metrics = self.fetch(
            interval or max(1.0, (now - worker.time).total_seconds())
        )
        self.save(worker, **sys_metrics, connected=True, time=now)
        if record:
            from .models import WorkerMonitor

            WorkerMonitor.objects.create(
                worker=worker,
                interval=interval,
                time=now,
                **sys_metrics,
                **req_metrics,
            )


worker_logger = WorkerMetricsLogger()
request_logger = var.RequestContextVar("_logger", cached=True, static=True)


class LogLevel:
    DEBUG = 0
    INFO = 1
    WARN = 2
    ERROR = 3


LOG_LEVELS = ["DEBUG", "INFO", "WARN", "ERROR"]


def level_log(f):
    lv = f.__name__.upper()
    if lv not in LOG_LEVELS:
        raise ValueError(f"Invalid log level: {lv}")
    index = LOG_LEVELS.index(lv)

    @wraps(f)
    def emit(self: "Logger", brief: str, msg: str = None, **kwargs):
        return self.emit(brief, level=index, data=kwargs, msg=msg)

    return emit


# def is_worker_primary():
#     if not _worker:
#         return
#     if not _instance:
#         return
#     from .models import Worker
#     worker: Worker = _worker    # NOQA
#     return not Worker.objects.filter(
#         instance=_instance,
#         connected=True,
#         pid__lt=worker.pid
#     ).exists()


def setup_locals(config: Operations, close_conn: bool = False):
    from .models import Resource, Worker, Supervisor
    from utilmeta import service

    global _worker, _supervisor, _instance, _server, _endpoints_map, \
        _openapi, _endpoints_patterns, _path_prefix, _databases, _caches
    # node_id = config.node_id
    _supervisor = Supervisor.current().first()
    # reset supervisor
    if _supervisor:
        node_id = _supervisor.node_id
    else:
        node_id = None

    if not _server:
        _server = Resource.get_current_server()
        from .monitor import get_current_server

        data = get_current_server()
        if not _server:
            from utilmeta.utils import get_mac_address

            mac = get_mac_address()
            _server = Resource.objects.create(
                type="server",
                service=None,
                # server is a service-neutral resource
                node_id=node_id,
                ident=mac,
                data=data,
                route=f"server/{mac}",
            )
        else:
            if _server.data != data:
                _server.data = data
                _server.save(update_fields=["data"])

    if not _instance:
        _instance = Resource.get_current_instance()
        from .schema import get_current_instance_data

        data = get_current_instance_data()
        if not _instance:
            ident = config.address
            _instance = Resource.objects.create(
                type="instance",
                service=service.name,
                node_id=node_id,
                ident=ident,
                route=f"instance/{node_id}/{ident}" if node_id else f"instance/{ident}",
                server=_server,
                data=data,
            )
        else:
            if _instance.data != data:
                _instance.data = data
                _instance.save(update_fields=["data"])

    # if not _version:
    #     if _instance:
    #         _version = VersionLog.objects.create(
    #             instance=_instance,
    #             version=service.version_str,
    #             service=service.name,
    #             node_id=node_id,
    #         )

    if not _worker:
        import utilmeta

        if not utilmeta._cmd_env:
            _worker = Worker.load()

    if not _endpoints_map:
        _endpoints = Resource.filter(
            type="endpoint", service=service.name, deprecated=False
        )

        if node_id:
            _endpoints = _endpoints.filter(node_id=node_id)

        _endpoints_map = {res.ident: res for res in _endpoints if res.ident}

    if not _openapi:
        # path-regex: ident
        _openapi = config.openapi
        from utilmeta.core.api.specs.openapi import get_operation_id
        from utilmeta.core.api.route import APIRoute

        patterns = {}
        operation_ids = []
        for path, path_item in _openapi.paths.items():
            if not path_item:
                continue
            try:
                pattern = APIRoute.get_pattern(path)
                methods = {}
                for method in HTTP_METHODS_LOWER:
                    operation = path_item.get(method)
                    if not operation:
                        continue
                    operation_id = operation.get("operationId")
                    if not operation_id:
                        operation_id = get_operation_id(
                            method, path, excludes=operation_ids, attribute=True
                        )
                    operation_ids.append(operation_id)
                    methods[method] = operation_id
                if methods:
                    patterns[pattern] = methods
            except Exception as e:
                warnings.warn(
                    f"generate pattern operation Id at path {path} failed: {e}"
                )
                continue

        _endpoints_patterns = patterns
        if _openapi.servers:
            url = _openapi.servers[0].url
            from urllib.parse import urlparse

            _path_prefix = urlparse(url).path.strip("/")

    if not _databases:
        from utilmeta.core.orm import DatabaseConnections

        db_config = DatabaseConnections.config()
        dbs = {}
        if db_config and db_config.databases:
            for alias, db in db_config.databases.items():
                db_obj = Resource.filter(
                    type="database", service=service.name, ident=alias, deprecated=False
                ).first()
                if not db_obj:
                    db_obj = Resource.objects.create(
                        type="database",
                        service=service.name,
                        node_id=node_id,
                        ident=alias,
                        route=f"database/{node_id}/{alias}"
                        if node_id
                        else f"database/{alias}",
                        server=_server if db.local else None,
                    )
                dbs[alias] = db_obj
            _databases = dbs

    if not _caches:
        from utilmeta.core.cache import CacheConnections

        cache_config = CacheConnections.config()
        caches = {}
        if cache_config and cache_config.caches:
            for alias, cache in cache_config.caches.items():
                if cache.is_memory:
                    # do not monitor memory cache for now
                    continue
                cache_obj = Resource.filter(
                    type="cache", service=service.name, ident=alias, deprecated=False
                ).first()
                if not cache_obj:
                    cache_obj = Resource.objects.create(
                        type="cache",
                        service=service.name,
                        node_id=node_id,
                        ident=alias,
                        route=f"cache/{node_id}/{alias}"
                        if node_id
                        else f"cache/{alias}",
                        server=_server if cache.local else None,
                    )
                caches[alias] = cache_obj
            _caches = caches

    if close_conn:
        # close connections
        from django.db import connections

        # ops_conn = connections[config.db_alias]
        # if ops_conn:
        #     ops_conn.close()
        connections.close_all()


class LogMiddleware(ServiceMiddleware):
    def __init__(self, config: Operations):
        super().__init__(config=config)
        self.config = config

    def process_request(self, request: Request):
        # log = request_logger.setup(request)
        # log.set(Logger())   # set logger
        logger = self.config.logger_cls()
        _logger.set(logger)
        logger.setup_request(request)
        request_logger.setter(request, logger)

    def is_excluded(self, response: Response):
        request = response.request
        if request:
            if self.config.log.exclude_methods:
                if (
                    request.adaptor.request_method.upper()
                    in self.config.log.exclude_methods
                ):
                    return True
            if self.config.log.exclude_request_headers:
                if any(
                    h in self.config.log.exclude_request_headers
                    for h in request.headers
                ):
                    return True
        else:
            return True
        if self.config.log.exclude_statuses:
            if response.status in self.config.log.exclude_statuses:
                return True
        if self.config.log.exclude_response_headers:
            if any(
                h in self.config.log.exclude_response_headers for h in response.headers
            ):
                return True
        return False

    def process_response(self, response: Response):
        logger: Logger = _logger.get(None)
        if not logger:
            return response.close()
        if not response.request:
            return response.close()

        logger.exit()
        logger.setup_response(response)

        # log metrics into current worker
        # even if the request is omitted
        worker_logger.log(
            duration=response.duration_ms,
            error=response.status >= 500,
            in_traffic=response.request.traffic,
            out_traffic=response.traffic,
        )

        if logger.omitted:
            return response.close()

        if self.is_excluded(response) or logger.events_only:
            if response.success and logger.vacuum:
                return response.close()

        _responses_queue.append(response)

        if len(_responses_queue) >= self.config.max_backlog:
            threading.Thread(target=batch_save_logs, kwargs=dict(close=True)).start()

    # def handle_error(self, error: Error, response=None):
    #     logger: Logger = _logger.get(None)
    #     if not logger:
    #         raise error.throw()
    #     logger.commit_error(error)


class Logger(Property):
    __context__ = ContextProperty(_logger)

    middleware_cls = LogMiddleware

    # DEFAULT_VOLATILE = True
    # EXCLUDED_METHODS = (HTTPMethod.OPTIONS, HTTPMethod.CONNECT, HTTPMethod.TRACE, HTTPMethod.HEAD)
    # VIOLATE_MAINTAIN: timedelta = timedelta(days=1)
    # MAINTAIN: timedelta = timedelta(days=30)        # ALL LOGS
    # PERSIST_DURATION = timedelta(seconds=1)
    # PERSIST_LEVEL = LogLevel.WARN
    # STORE_DATA_LEVEL = LogLevel.WARN
    # STORE_RESULT_LEVEL = LogLevel.WARN
    # STORE_HEADERS_LEVEL = LogLevel.WARN

    def __init__(self, from_logger: "Logger" = None, span_data: dict = None):
        super().__init__()
        from utilmeta import service

        self.service = service
        self.config = service.get_config(Operations)
        self.current_thread = threading.current_thread().ident
        self.init_time = time.time()
        if from_logger:
            self.init_time = from_logger.init_time
        self.init = self.relative_time()
        self.duration = None

        self._request = None
        self._supervised = False
        self._from_logger = from_logger
        self._span_logger: Optional[Logger] = None
        self._span_data = span_data
        self._client_responses = []
        self._events = []
        self._messages = []
        self._briefs = []
        self._exceptions = []
        self._level = None
        self._omitted = False
        self._events_only = False
        self._server_timing = False
        self._exited = False
        self._volatile = self.config.log.default_volatile
        self._store_data_level = self.config.log.store_data_level
        self._store_result_level = self.config.log.store_result_level
        self._store_headers_level = self.config.log.store_headers_level
        self._persist_level = self.config.log.persist_level
        self._persist_duration_limit = self.config.log.persist_duration_limit
        if self._store_data_level is None:
            self._store_data_level = (
                LogLevel.WARN if service.production else LogLevel.INFO
            )
        if self._store_headers_level is None:
            self._store_headers_level = (
                LogLevel.WARN if service.production else LogLevel.INFO
            )
        if self._store_result_level is None:
            self._store_result_level = (
                LogLevel.WARN if service.production else LogLevel.INFO
            )

    def relative_time(self, to=None):
        return max(int(((to or time.time()) - self.init_time) * 1000), 0)

    @property
    def from_logger(self):
        return self._from_logger

    @property
    def omitted(self):
        return self._omitted

    @property
    def events_only(self):
        return self._events_only

    @property
    def vacuum(self):
        return (
            not self._messages
            and not self._events
            and not self._exceptions
            and not self._span_logger
        )

    @property
    def level(self):
        return self._level

    @property
    def messages(self):
        return self._messages

    @property
    def volatile(self):
        return self._volatile

    @volatile.setter
    def volatile(self, v):
        self._volatile = v

    @classmethod
    def status_level(cls, status: int):
        level = LogLevel.INFO
        if not status:
            level = LogLevel.ERROR
        elif status >= 500:
            level = LogLevel.ERROR
        elif status >= 400:
            level = LogLevel.WARN
        return level

    def __call__(self, name: str, **kwargs):
        if self._span_logger:
            return self._span_logger(name, **kwargs)
        assert name, f"Empty scope name"
        self._span_data = dict(name=name, **kwargs)
        return self

    def __enter__(self) -> "Logger":
        if self._span_logger:
            return self._span_logger.__enter__()
        if not self._span_data:
            return self
        data = dict(self._span_data)
        self._events.append(data)
        logger = Logger(
            span_data=data,
            from_logger=self,
        )
        logger._request = self._request
        logger._supervised = self._supervised
        logger._server_timing = self._server_timing
        _logger.set(logger)
        self._span_logger = logger
        return logger

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self._span_logger:
            return
        self._span_logger: Logger
        self._span_logger.exit()
        # self._events.append(self._span_logger.span)
        if self._span_data:
            # update
            self._span_data.update(self._span_logger.span)
        self._span_logger = None

    @property
    def span(self):
        data = dict(
            init=self.init,
            time=self.duration,
            events=self._events,
        )
        # if self._queries_num:
        #     data.update(
        #         queries=self._queries_num,
        #         queries_time=self._queries_duration,
        #     )
        # if self._outbound_requests_num:
        #     data.update(
        #         outbound_requests=self._outbound_requests_num,
        #         outbound_requests_time=self._outbound_duration,
        #     )
        return data

    def setup_request(self, request: Request):
        self._request = request
        if _supervisor:
            supervisor_id = request.headers.get(
                "x-utilmeta-node-id"
            ) or request.headers.get("x-node-id")
            supervisor_hash = request.headers.get("X-utilmeta-supervisor-key-md5")
            if supervisor_hash and supervisor_id == _supervisor.node_id:  # noqa
                import hashlib

                if hashlib.md5(_supervisor.public_key) == supervisor_hash:  # noqa
                    self._supervised = True
        if self._supervised:
            log_options = request.headers.get("x-utilmeta-log-options")
            if log_options:
                options = [
                    option.strip() for option in str(log_options).lower().split(",")
                ]
                if "omit" in options:
                    self._omitted = True
                if "timing" in options or "server-timing" in options:
                    self._server_timing = True

    def omit(self, val: bool = True):
        self._omitted = val

    def make_events_only(self, val: bool = True):
        self._events_only = val

    def setup_response(self, response: Response):
        if self._supervised:
            if self._server_timing:
                duration = response.duration_ms or self.duration
                ts = (
                    response.request.time.timestamp()
                    if response.request
                    else self.init_time
                )
                if duration:
                    response.set_header(
                        "Server-Timing", f"total;dur={duration};ts={ts}"
                    )

    def generate_request_logs(self, context_type="service_log", context_id=None):
        if not self._client_responses:
            return []

        objects = []

        for resp in self._client_responses:
            log = self.generate_request_log(
                resp, context_type=context_type, context_id=context_id
            )
            if log:
                objects.append(log)
        return objects

    def generate_request_log(
        self, response: Response, context_type="service_log", context_id=None
    ):
        from .models import RequestLog

        return RequestLog()

    @classmethod
    def get_file_repr(cls, file):
        return "<file>"

    def parse_values(self, data):
        return hide_secret_values(
            data, secret_names=self.config.secret_names, file_repr=self.get_file_repr
        )

    @classmethod
    def get_endpoint_ident(cls, request: Request) -> Optional[str]:
        if not _endpoints_patterns:
            return None
        path = str(request.path or "").strip("/")
        if _path_prefix:
            if not path.startswith(_path_prefix):
                return None
            path = path[len(_path_prefix) :].strip("/")
        for pattern, methods in _endpoints_patterns.items():
            if pattern.fullmatch(path):
                return methods.get(request.method)
        return None

    def generate_log(self, response: Response):
        from utilmeta.ops.models import ServiceLog
        from .api import access_token_var

        request = response.request
        duration = response.duration_ms

        status = response.status
        path = request.path
        in_traffic = request.traffic
        out_traffic = response.traffic
        level = self.level
        if level is None:
            level = self.status_level(status)

        if response.error:
            self.commit_error(response.error)

        method = str(request.adaptor.request_method).lower()
        user_id = var.user_id.getter(request, default=None)
        query = self.parse_values(request.query or {})
        data = None
        result = None

        if level >= self._store_data_level:
            if method in HAS_BODY_METHODS:
                # if data should be saved
                try:
                    data = self.parse_values(request.data)
                except Exception as e:  # noqa: ignore
                    warnings.warn(f"load request data failed: {e}")

        if level >= self._store_result_level:
            try:
                result = self.parse_values(response.data)
            except Exception as e:  # noqa: ignore
                warnings.warn(f"load response data failed: {e}")

        try:
            public = request.ip_address.is_global
        except ValueError:
            public = False

        volatile = self.volatile
        if level >= self._persist_level:
            volatile = False
        if self._persist_duration_limit:
            if duration and duration >= self._persist_duration_limit * 1000:
                volatile = False

        request_headers = {}
        response_headers = {}
        if level >= self._store_headers_level:
            request_headers = self.parse_values(dict(request.headers))
            response_headers = self.parse_values(
                dict(response.prepare_headers(with_content_type=True))
            )

        operation_names = var.operation_names.getter(request)
        if operation_names:
            endpoint_ident = "_".join(operation_names)
        else:
            # or find it by the generated openapi items (match method and path, find operationId)
            endpoint_ident = self.get_endpoint_ident(request)

        endpoint_ref = var.endpoint_ref.getter(request) or None
        endpoint = _endpoints_map.get(endpoint_ident) if endpoint_ident else None
        access_token = access_token_var.getter(request)

        try:
            level_str = LOG_LEVELS[level]
        except IndexError:
            level_str = LogLevel.DEBUG

        return ServiceLog(
            service=self.service.name,
            instance=_instance,
            version=_version,
            node_id=getattr(_supervisor, "node_id", None),
            supervisor=_supervisor,
            access_token_id=getattr(access_token, "id", None),
            level=level_str,
            volatile=volatile,
            time=request.time,
            duration=duration,
            worker=_worker,
            scheme=request.scheme,
            thread_id=self.current_thread,
            in_traffic=in_traffic,
            out_traffic=out_traffic,
            public=public,
            path=path,
            full_url=request.url,
            query=query,
            data=data,
            result=result,
            user_id=str(user_id)[:100] if user_id else None,
            ip=str(request.ip_address),
            user_agent=parse_user_agents(request.headers.get("user-agent")),
            status=status,
            request_type=str(request.content_type)[:200] if request.content_type else None,
            response_type=str(response.content_type)[:200] if response.content_type else None,
            request_headers=request_headers,
            response_headers=response_headers,
            length=response.content_length,
            method=method,
            endpoint=endpoint,
            endpoint_ident=str(endpoint_ident)[:200] if endpoint_ident else None,
            endpoint_ref=str(endpoint_ref)[:200] if endpoint_ref else None,
            messages=self.messages,
            trace=self.get_trace(),
        )

    def get_trace(self):
        self._events.sort(key=lambda v: v.get("init", 0))
        return normalize(self._events, _json=True)

    def exit(self):
        if self._exited:
            return
        self._exited = True
        if self.duration is None:
            # forbid to recalculate
            self.duration = self.relative_time() - self.init

        if self._span_logger:
            self._span_logger.exit()

        if self.from_logger:
            if self._span_data:
                self._span_data.update(self.span)

            _logger.set(self.from_logger)
        else:
            _logger.set(None)

    def emit(
        self, brief: Union[str, Error], level: int, data: dict = None, msg: str = None
    ):
        if self._span_logger:
            return self._span_logger.emit(brief, level, data, msg=msg)

        exception = None
        ts = None
        if isinstance(brief, Exception):
            exception = brief
            brief = Error(brief)

        if isinstance(brief, Error):
            brief.setup()
            ts = brief.ts
            exception = brief.exception
            msg = brief.message
            brief = str(brief)

        if not level:
            level = LogLevel.INFO

        if self._level is None:
            self._level = level
        else:
            if self._level < level:
                self._level = level

        if exception:
            self._exceptions.append(exception)

        name = LOG_LEVELS[level]
        self._events.append(
            dict(
                name=name,
                init=self.relative_time(ts),
                type=f"log.{name.lower()}",
                msg=self._push_message(brief, msg=msg),
                data=data,
            )
        )

    def commit_error(self, e: Error):
        if e.exception in self._exceptions:
            return
        self._exceptions.append(e.exception)
        level = self.status_level(e.status)
        self.emit(e, level=level)

    def _push_message(self, brief: str, msg: str = None):
        brief = str(brief)
        msg = str(msg or brief)
        if not msg:
            return None
        if self.from_logger:
            return self.from_logger._push_message(brief, msg)
        if brief not in self._briefs:
            self._briefs.append(brief)
        if msg not in self._messages:
            self._messages.append(msg)
        return self._messages.index(msg)

    @level_log
    def debug(self, brief: Union[str, Exception], msg: str = None, **kwargs):
        pass

    @level_log
    def info(self, brief: Union[str, Exception], msg: str = None, **kwargs):
        pass

    @level_log
    def warn(self, brief: Union[str, Exception], msg: str = None, **kwargs):
        pass

    @level_log
    def error(self, brief: Union[str, Exception], msg: str = None, **kwargs):
        pass

    @property
    def message(self) -> str:
        return "\n".join(self._messages)

    @property
    def brief_message(self) -> str:
        return "; ".join(self._briefs)


def batch_save_logs(close: bool = False):
    from utilmeta.ops.models import ServiceLog, QueryLog, RequestLog

    with threading.Lock():
        global _responses_queue, _supervisor
        queue = _responses_queue
        _responses_queue = []
        # ----------------
        logs_creates = []
        logs_updates = []
        query_logs = []
        request_logs = []

        if not _server:
            # not setup yet
            from .config import Operations

            setup_locals(Operations.config())

        if _supervisor:
            # update supervisor (connect / disconnect)
            from .models import Supervisor

            supervisor = Supervisor.objects.filter(
                pk=getattr(_supervisor, "pk", None)
            ).first()
            if not supervisor:
                # check _supervisor before save logs
                _supervisor = None
            else:
                _supervisor = supervisor

        for response in queue:
            response: Response
            try:
                logger: Logger = request_logger.getter(response.request)
                if not logger:
                    continue

                service_log = logger.generate_log(response)

                if not service_log:
                    continue

                if service_log.id:
                    logs_updates.append(service_log)
                else:
                    logs_creates.append(service_log)
            finally:
                response.close()

        if not logs_creates and not logs_updates:
            return

        if logs_updates:
            for log in logs_updates:
                log.save()

        if logs_creates:
            ServiceLog.objects.bulk_create(logs_creates, ignore_conflicts=True)

        if query_logs:
            QueryLog.objects.bulk_create(query_logs, ignore_conflicts=True)

        if request_logs:
            RequestLog.objects.bulk_create(request_logs, ignore_conflicts=True)

    if close:
        from django.db import connections

        connections.close_all()

    return


def omit_log():
    pass
