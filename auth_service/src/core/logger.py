import logging
import uuid

from src.core.config import settings
from src.core.context import ctx_request_id

LOG_FORMAT = '{"request_id": "%(request_id)s", "asctime": \
             "%(asctime)s", "levelname": "%(levelname)s", \
             "name": "%(name)s", "message": "%(message)s", \
             "host": "%(host)s", "user-agent": "%(user-agent)s", "method": "%(method)s", "path": "%(path)s", \
             "query_params": "%(query_params)s", "status_code": "%(status_code)s"}'


def setup_root_logger():
    root_logger = logging.getLogger("")
    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    app_logger = logging.getLogger("app_logger")
    formatter = logging.Formatter(LOG_FORMAT)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    file = logging.handlers.RotatingFileHandler(  # type: ignore[attr-defined]
        filename=settings.logging.logger_filename,
        mode=settings.logging.logger_mod,
        maxBytes=settings.logging.logger_maxbytes,
        backupCount=settings.logging.logger_backup_count,
    )
    file.setFormatter(formatter)
    app_logger.addHandler(console_handler)
    app_logger.addHandler(file)
    app_logger.setLevel(logging.INFO)

    factory = logging.getLogRecordFactory()

    def record_factory(*args, **kwargs):
        record = factory(*args, **kwargs)
        record.request_id = ctx_request_id.get(uuid.uuid4())
        return record

    logging.setLogRecordFactory(record_factory)


LOG_DEFAULT_HANDLERS = ["console"]

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {"format": LOG_FORMAT},
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": "%(levelprefix)s %(message)s",
            "use_colors": None,
        },
        "access": {
            "()": "uvicorn.logging.AccessFormatter",
            "fmt": "%(levelprefix)s %(client_addr)s - '%(request_line)s' %(status_code)s",
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
        "access": {
            "formatter": "access",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {
        "": {"handlers": LOG_DEFAULT_HANDLERS, "level": "INFO"},
        "uvicorn.error": {"level": "INFO"},
        "uvicorn.access": {
            "handlers": ["access"],
            "level": "INFO",
            "propagate": False,
        },
    },
    "root": {
        "level": "INFO",
        "formatter": "verbose",
        "handlers": LOG_DEFAULT_HANDLERS,
    },
}

logger = logging.getLogger("app_logger")
