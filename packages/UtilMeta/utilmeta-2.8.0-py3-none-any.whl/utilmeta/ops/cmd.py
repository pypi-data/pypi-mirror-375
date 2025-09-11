import time

from utilmeta.bin.commands.base import BaseServiceCommand
from utilmeta.bin.base import command
from .config import Operations
from utilmeta.bin.base import Arg
from utilmeta.utils import omit
from . import __website__
from utilmeta.bin.constant import DOT, RED, GREEN, BANNER, BLUE, YELLOW
import webbrowser


@omit
def try_to_connect(timeout: int = 5):
    config = Operations.config()
    if not config:
        return
    if not config.is_local:
        webbrowser.open_new_tab(__website__)
        print(
            RED
            % f"connection key required to connect non-local service, please login to "
            f"{__website__} and generate one"
        )
        return
    from utilmeta.ops.client import OperationsClient, ServiceInfoResponse

    t = time.time()
    live = False
    while True:
        if time.time() - t > timeout:
            break
        info = OperationsClient(base_url=config.ops_api, fail_silently=True).get_info()
        live = isinstance(info, ServiceInfoResponse) and info.validate()
        if not live:
            time.sleep(0.5)
        else:
            break
    if not live:
        print(
            RED % "meta connect: service not live or OperationsAPI not mounted, "
            f"please check your OperationsAPI: {config.ops_api} is accessible before connect"
        )
        return
    local_manage_url = config.connect_url
    print(f"OperationsAPI connected at {local_manage_url}")
    webbrowser.open_new_tab(local_manage_url)


class OperationsCommand(BaseServiceCommand):
    name = "ops"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config = self.service.get_config(Operations)
        if not self.config:
            print(
                RED
                % f"meta {self.arg_name}: Operations config not integrated to application, "
                "please follow the document at https://docs.utilmeta.com/py/en/guide/ops/"
            )
            exit(1)
        # self.settings.setup(self.service)
        self.service.setup()  # setup here

    @command
    def migrate_ops(self):
        """
        Migrate all required tables for UtilMeta Operations to the database
        """
        from django.core.management import execute_from_command_line

        execute_from_command_line(
            ["manage.py", "migrate", "ops", f"--database={self.config.db_alias}"]
        )
        # 2. migrate for main database
        execute_from_command_line(["manage.py", "migrate", "ops"])

    # @command
    # def check_connect(self):
    #     if not self.config:
    #         print(RED % 'meta check_ops: Operations config not integrated to application, '
    #                     'please follow the document')
    #         exit(1)
    #     self.config.migrate(with_default=True)
    #     # before check
    #
    #     from .client import OperationsClient, ServiceInfoResponse
    #     info = OperationsClient(base_url=self.config.ops_api, fail_silently=True).get_info()
    #     live = isinstance(info, ServiceInfoResponse) and info.validate()
    #     if live:
    #         print(f'meta connect: OperationsAPI of [{self.service.name}] '
    #               f'is available at {BLUE % self.config.ops_api}')

    @command
    def connect(
        self,
        to: str = None,
        key: str = Arg("--key", default=None),
        force: bool = Arg("-f", default=None),
        service: str = Arg("--service", default=None),
    ):
        """
        Connect your API service to UtilMeta platform to manage
        """
        self.config.migrate(with_default=True)
        # before connect

        # check if service is live
        from .client import OperationsClient, ServiceInfoResponse

        info = OperationsClient(
            base_url=self.config.ops_api, fail_silently=True
        ).get_info()
        live = isinstance(info, ServiceInfoResponse) and info.validate()
        failed = info.is_aborted or info.status >= 500
        if not live:
            error_message = str(info)
            if info.is_timeout:
                error_message = "connect timeout"
            elif info.is_aborted:
                error_message = "connect failed"
            elif info.success:
                error_message = "response data syntax error"

            if failed:
                print(
                    RED % f"meta connect: service is down ({error_message}), "
                    f"please check your OperationsAPI: {self.config.ops_api} is accessible before connect"
                )
            else:
                print(
                    YELLOW
                    % f"meta connect: OperationsAPI not mounted or service not reloaded (got {error_message}), "
                    f"please check your OperationsAPI: {self.config.ops_api} is accessible before connect"
                )
            print(
                "If you have integrated Operations config, please restart your service and retry, "
                f'or add {BLUE % "-f"} argument to force this connect'
            )
            if not force:
                exit(1)

        if not key:
            # check if it is localhost
            if self.config.is_local:
                local_manage_url = self.config.connect_url
                print(f"OperationsAPI connected at {local_manage_url}")
                webbrowser.open_new_tab(local_manage_url)
                exit(0)

        if not self.config.is_local:
            if not self.config.proxy:
                if self.config.proxy_required:
                    print(
                        YELLOW
                        % f"meta connect: it seems that you are using a private base_url: {self.config.base_url} "
                        f"without setting "
                        "a proxy in Operations, this service will be unable to access in the platform"
                    )

                if not self.config.is_secure:
                    print(
                        YELLOW
                        % f"meta connect: you are trying to connect an insecure node:"
                        f" {self.config.ops_api} (with HTTP protocol), "
                        "we strongly recommend using HTTPS protocol instead"
                    )

        if self.config.proxy:
            print(f"Connect to supervisor using proxy: {self.config.proxy.base_url}")
            manager = self.config.resources_manager_cls(service=self.service)
            node_id = manager.init_service_resources(force=force)
            if node_id:
                from .models import Supervisor

                supervisor: Supervisor = Supervisor.filter(node_id=node_id).first()
                if supervisor:
                    print(f"UtilMeta supervisor[{node_id}] connected")
                    if supervisor.url:
                        print(
                            f"please visit {supervisor.url} to view and manage your APIs"
                        )
            return

        if not key:
            webbrowser.open_new_tab(__website__)
            if live:
                print(
                    f"meta connect: OperationsAPI of [{self.service.name}] "
                    f"is available at {BLUE % self.config.ops_api}"
                )
            print(
                RED
                % f"meta connect: --key is required to connect non-local service, please login to "
                f"{__website__} and generate one"
            )

            exit(1)

        from .connect import connect_supervisor

        connect_supervisor(key=key, base_url=to, service_id=service)

    @command
    def delete_supervisor(
        self, node: str = Arg(required=True), key: str = Arg("--key", required=True)
    ):
        """
        Connect your API service to UtilMeta platform to manage
        """
        # self.migrate_ops()
        # before connect
        from .connect import delete_supervisor

        delete_supervisor(key=key, node_id=node)

    @command
    def sync(self, force: bool = Arg("-f", default=False)):
        """
        Sync APIs and resources to supervisor
        """
        manager = self.config.resources_manager_cls(service=self.service)
        manager.init_service_resources(force=force)

    @command
    def stats(self):
        """
        View the current service stats
        """
        self.config.migrate(with_default=True)
        from .log import setup_locals

        setup_locals(self.config)
        from .client import OperationsClient, ServiceInfoResponse

        info = OperationsClient(
            base_url=self.config.ops_api, fail_silently=True
        ).get_info()
        live = isinstance(info, ServiceInfoResponse) and info.validate()
        from utilmeta.utils import readable_size
        import utilmeta
        from . import __website__
        from .log import _instance, _databases, _caches, _supervisor

        stage_str = "production" if self.service.production else "debug"
        status_str = (GREEN % f"{DOT} live") if live else (RED % f"{DOT} down")
        supervisor_str = (
            BLUE % f"{_supervisor.url}"
            if _supervisor
            else f"not connected (connect at {__website__})"
        )
        print(
            BANNER
            % "{:<60}".format(f"UtilMeta v{utilmeta.__version__} Operations Stats")
        )
        print(
            f"      Service Name: {self.service.name}",
            f"({self.service.title})" if self.service.title else "",
        )
        print(f"   Service Version: {self.service.version_str}")
        print(f"    Service Status: {status_str} ({stage_str})")
        print(
            f"   Service Backend:",
            f"{self.service.backend_name} ({self.service.backend_version})",
            (BLUE % f"| asynchronous") if self.service.asynchronous else "",
        )
        print(f"  Service Base URL: {self.config.base_url}")
        print(f" OperationsAPI URL: {self.config.ops_api}")
        print(f"     UtilMeta Node: {supervisor_str}")

        print(BANNER % "{:<60}".format("Service Instance Stats"))

        from .models import InstanceMonitor, Worker, DatabaseMonitor, CacheMonitor
        from .query import (
            InstanceMonitorSchema,
            DatabaseMonitorSchema,
            CacheMonitorSchema,
            WorkerSchema,
        )
        from utilmeta.core import orm, cache

        latest_monitor = None
        workers = []
        if _instance:
            try:
                latest_monitor = InstanceMonitorSchema.init(
                    InstanceMonitor.objects.filter(
                        instance=_instance, layer=0
                    ).order_by("-time")
                )
            except orm.EmptyQueryset:
                pass
            workers = WorkerSchema.serialize(
                Worker.objects.filter(instance=_instance, connected=True).order_by(
                    "-requests"
                )
            )

        if latest_monitor:
            record_ago = int(time.time() - latest_monitor.time)
            print(
                f"       Stats Cycle: {latest_monitor.interval} seconds (recorded {record_ago}s ago)"
            )
            print(
                f"          Requests: {latest_monitor.requests} ({latest_monitor.rps} per second)"
            )
            if latest_monitor.errors:
                print(RED % f"            Errors: {latest_monitor.errors}")
            print(f"          Avg Time: {round(latest_monitor.avg_time, 1)} ms")
            print(
                f"           Traffic: {readable_size(latest_monitor.in_traffic)} In / "
                f"{readable_size(latest_monitor.out_traffic)} Out"
            )
            print(
                f"       Used Memory: {readable_size(latest_monitor.used_memory)} ({latest_monitor.memory_percent}%)"
            )
            print(f"               CPU: {latest_monitor.cpu_percent}%")
            print(
                f"          Net conn: {latest_monitor.total_net_connections} "
                f"({latest_monitor.active_net_connections} active)"
            )
        if workers:
            print(BANNER % "{:<60}".format("Service Instance Workers"))
            fields = (
                "PID",
                "Status",
                "Threads",
                "Requests",
                "Avg Time",
                "Traffic",
                "CPU",
                "Memory",
            )
            form = "{:<10}{:<15}{:<10}{:<25}{:<15}{:<25}{:<8}{:<10}"
            print(form.format(*fields))
            print("-" * 60)
            for worker in workers:
                print(
                    form.format(
                        worker.pid,
                        f"{DOT} {worker.status}",
                        worker.threads,
                        f"{worker.requests} ({worker.rps} per second)",
                        f"{worker.avg_time} ms",
                        f"{readable_size(worker.in_traffic)} In / {readable_size(worker.out_traffic)} Out",
                        f"{worker.cpu_percent}%",
                        f"{readable_size(worker.used_memory)} ({worker.memory_percent}%)",
                    )
                )

        if _databases:
            from utilmeta.core.orm import DatabaseConnections

            db_config = DatabaseConnections.config()
            if db_config:
                print(BANNER % "{:<60}".format("Service Instance Databases"))
                fields = ("Alias", "Engine", "Name", "Connections", "Space", "Location")
                form = "{:<15}{:<15}{:<15}{:<25}{:<15}{:<50}"
                print(form.format(*fields))
                print("-" * 60)
                for alias, database in _databases.items():
                    db = db_config.get(alias)
                    if not db:
                        continue
                    conn_str = ""
                    space_str = ""
                    max_connections = database.data.get("max_server_connections")
                    try:
                        latest_monitor = DatabaseMonitorSchema.init(
                            DatabaseMonitor.objects.filter(
                                database=database, layer=0
                            ).order_by("-time")
                        )
                    except orm.EmptyQueryset:
                        pass
                    else:
                        conn_str = (
                            f"{latest_monitor.current_connections} "
                            f"({latest_monitor.active_connections} active)"
                        )
                        if max_connections:
                            conn_str += f" / {max_connections}"
                        space_str = f"{readable_size(latest_monitor.used_space)}"
                    print(
                        form.format(
                            alias,
                            db.type or "-",
                            db.database_name or "-",
                            conn_str,
                            space_str,
                            db.location or "-",
                        )
                    )

        if _caches:
            cache_config = cache.CacheConnections.config()
            if cache_config:
                print(BANNER % "{:<60}".format("Service Instance Caches"))
                fields = (
                    "Alias",
                    "Engine",
                    "PID",
                    "Connections",
                    "Memory",
                    "CPU",
                    "Location",
                )
                form = "{:<15}{:<15}{:<15}{:<25}{:<15}{:<15}{:<30}"
                print(form.format(*fields))
                print("-" * 60)
                for alias, cache_obj in _caches.items():
                    cache = cache_config.get(alias)
                    if not cache:
                        continue
                    pid = cache_obj.data.get("pid") or "--"
                    mem_str = ""
                    conn_str = ""
                    cpu_str = ""
                    loc_str = (
                        f"{cache.host}:{cache.port}"
                        if (cache.host and cache.port)
                        else ""
                    )
                    try:
                        latest_monitor = CacheMonitorSchema.init(
                            CacheMonitor.objects.filter(
                                cache=cache_obj, layer=0
                            ).order_by("-time")
                        )
                    except orm.EmptyQueryset:
                        pass
                    else:
                        conn_str = (
                            f"{latest_monitor.current_connections} "
                            f"({latest_monitor.total_connections} total)"
                        )
                        mem_str = f"{readable_size(latest_monitor.used_memory)}"
                        if latest_monitor.memory_percent:
                            mem_str += f" ({latest_monitor.memory_percent}%)"
                        cpu_str = (
                            f"{latest_monitor.cpu_percent}%"
                            if latest_monitor.cpu_percent is not None
                            else "-"
                        )

                    print(
                        form.format(
                            alias, cache.type, pid, conn_str, mem_str, cpu_str, loc_str
                        )
                    )
