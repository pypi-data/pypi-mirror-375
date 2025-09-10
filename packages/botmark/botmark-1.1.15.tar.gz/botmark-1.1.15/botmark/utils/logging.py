import os
import json
import logging
import contextvars
from logging.handlers import TimedRotatingFileHandler

# ---------- Context (request ID) ----------
request_id_var = contextvars.ContextVar("request_id", default="-")

def set_request_id(value: str) -> None:
    request_id_var.set(value)

class RequestIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_var.get()
        return True

# ---------- JSON Formatter ----------
class JsonFormatter(logging.Formatter):
    _reserved = {
        "name","msg","args","levelname","levelno","pathname","filename","module",
        "exc_info","exc_text","stack_info","lineno","funcName","created","msecs",
        "relativeCreated","thread","threadName","processName","process","message"
    }

    def format(self, record: logging.LogRecord) -> str:
        base = {
            "time": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": getattr(record, "request_id", "-"),
        }
        # Attach extra fields
        for k, v in record.__dict__.items():
            if k not in self._reserved and not k.startswith("_"):
                base[k] = v
        # Exceptions
        if record.exc_info:
            base["exc"] = self.formatException(record.exc_info)
        if record.stack_info:
            base["stack"] = record.stack_info
        return json.dumps(base, ensure_ascii=False)

# ---------- Setup function ----------
def setup_logging(
    *,
    name: str = "botmark",
    level: str | int | None = None,
    console_level: str | int | None = None,
    logfile: str | None = "logs/botmark.log",
    json_console: bool | None = None,
    json_file: bool | None = None,
) -> logging.Logger:
    """
    Initialize logging for the app.

    ENV variables:
      LOG_LEVEL=INFO|DEBUG|WARNING|ERROR
      LOG_CONSOLE_LEVEL=...
      LOG_JSON_CONSOLE=true|false
      LOG_JSON_FILE=true|false
      LOG_FILE=path/to/file.log (empty = disable file logging)
    """
    root = logging.getLogger()
    if getattr(root, "_botmark_configured", False):
        return logging.getLogger(name)

    # Environment overrides
    level = level or os.getenv("LOG_LEVEL", "WARNING")
    console_level = console_level or os.getenv("LOG_CONSOLE_LEVEL", level)
    logfile = os.getenv("LOG_FILE", logfile)
    json_console = (os.getenv("LOG_JSON_CONSOLE", str(json_console or "false")).lower() == "true")
    json_file = (os.getenv("LOG_JSON_FILE", str(json_file or "false")).lower() == "true")

    root.setLevel(level)

    # Formatters
    text_fmt = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s %(request_id)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    json_fmt = JsonFormatter(datefmt="%Y-%m-%dT%H:%M:%S%z")

    # Request ID filter
    req_filter = RequestIdFilter()

    # Console handler
    sh = logging.StreamHandler()
    sh.setLevel(console_level)
    sh.addFilter(req_filter)
    sh.setFormatter(json_fmt if json_console else text_fmt)
    root.addHandler(sh)

    # File handler (rotating daily)
    if logfile:
        os.makedirs(os.path.dirname(logfile), exist_ok=True)
        fh = TimedRotatingFileHandler(
            logfile, when="midnight", backupCount=7, encoding="utf-8", utc=True
        )
        fh.setLevel(level)
        fh.addFilter(req_filter)
        fh.setFormatter(json_fmt if json_file else text_fmt)
        root.addHandler(fh)

    # Reduce noisy loggers
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)

    root._botmark_configured = True  # type: ignore[attr-defined]
    return logging.getLogger(name)
