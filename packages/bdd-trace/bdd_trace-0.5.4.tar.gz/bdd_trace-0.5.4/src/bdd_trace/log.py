import sys
from logging import INFO, Formatter, Handler, LogRecord, StreamHandler, getLogger
from logging.handlers import QueueHandler, QueueListener
from queue import Queue

from opentelemetry.sdk._logs import LoggingHandler

from bdd_trace.trace import Profile

_log_queue: Queue | None = None
_log_listener: QueueListener | None = None


def setup_logging(
    profile: Profile,
    modules: list[str],
    level: str | int = INFO,
    enable_console_log: bool = True,
    trace_id_format: str = "%(asctime)s|%(levelname)s|%(name)s|%(otelTraceID)s|%(message)s",
    no_trace_id_format: str = "%(asctime)s|%(levelname)s|%(name)s|%(message)s",
    extra_handlers: list[Handler] | None = None,
) -> None:
    global _log_queue, _log_listener
    if _log_queue is not None or _log_listener is not None:
        raise RuntimeError("logging is already setup")

    root_logger = getLogger()
    root_logger.handlers = []

    _log_queue = Queue(1000)
    log_process_handlers = extra_handlers or []

    for module in modules:
        origin_handlers = _setup_module_logger(level, module)
        for handler in origin_handlers:
            handler.addFilter(ModulePrefixFilter([module]))
            log_process_handlers.append(handler)

    if enable_console_log:
        format = trace_id_format if profile != Profile.NO_TRACE else no_trace_id_format
        console_handler = _create_console_handler(modules, format)
        log_process_handlers.append(console_handler)
    if profile != Profile.NO_TRACE:
        otel_handler = LoggingHandler()
        log_process_handlers.append(otel_handler)

    _log_listener = QueueListener(_log_queue, *log_process_handlers)
    _log_listener.start()


def stop_logging() -> None:
    global _log_queue, _log_listener
    if _log_listener is not None:
        _log_listener.stop()
    _log_listener = None
    _log_queue = None


class ModulePrefixFilter:
    def __init__(self, module_prefixes: list[str]):
        self.module_prefixes: set[str] = set(module_prefixes)
        self.module_prefixes_with_dot: tuple[str, ...] = tuple(f"{prefix}." for prefix in module_prefixes)

    def filter(self, record: LogRecord) -> bool:
        return record.name in self.module_prefixes or record.name.startswith(self.module_prefixes_with_dot)


class SingleLineFormatter(Formatter):
    def formatMessage(self, record: LogRecord) -> str:
        return super().formatMessage(record).replace("\n", " ").replace("\r", "")


def _create_console_handler(modules: list[str], format: str) -> Handler:
    handler = StreamHandler(sys.stderr)
    handler.setFormatter(Formatter(format))
    handler.addFilter(ModulePrefixFilter(modules))
    return handler


def _setup_module_logger(level: str | int, module: str) -> list[Handler]:
    logger = getLogger(module)
    logger.setLevel(level)
    logger.propagate = False

    queue = _log_queue
    if queue is None:
        raise RuntimeError("log queue is not initialized")
    handler = QueueHandler(queue)
    handler.setFormatter(SingleLineFormatter())
    origin_handlers = logger.handlers
    logger.handlers = [handler]
    return origin_handlers or []
