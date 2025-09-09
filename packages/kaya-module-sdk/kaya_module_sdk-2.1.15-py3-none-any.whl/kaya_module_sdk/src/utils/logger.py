import logging
import logging.config
import os
import json
import time

from logging import Logger, LoggerAdapter, LogRecord
from logging.handlers import RotatingFileHandler
from ddtrace import patch

# Module-level flag to avoid multiple setups
_dd_log_configured: bool = False
_dd_log: LoggerAdapter[Logger]


class DatadogJSONFormatter(logging.Formatter):
    """
    A simple JSON log formatter compatible with Datadog log ingestion.
    Includes dd.trace_id, dd.span_id, dd.env, dd.service, dd.version if available.
    """

    def format(self, record: LogRecord) -> str:
        log_record = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z", time.localtime(record.created)),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add Datadog correlation IDs if present
        for field in ("dd.trace_id", "dd.span_id", "dd.env", "dd.service", "dd.version"):
            value = getattr(record, field, None)
            if value is not None:
                log_record[field] = value

        # Add exception info if present
        if record.exc_info:
            log_record["exc_info"] = self.formatException(record.exc_info)

        return json.dumps(log_record)


def setup_datadog_logging(
    level: str,
    service: str,
    env: str,
    version: str,
    location: str | None = None,
    max_bytes: int = 10 * 1024 * 1024,  # 10 MB
    backup_count: int = 5,
    force: bool = False,
) -> LoggerAdapter[Logger]:
    """
    Sets up a base logging config (no per-class handlers yet).
    Logging target is chosen based on $STAGE:
      - DEV -> stdout only
      - PROD -> file only
      - STAGING -> both
    """

    global _dd_log_configured
    global _dd_log
    if force and _dd_log_configured:
        return _dd_log

    patch(logging=True)

    if level not in ("CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "NOTSET"):
        raise ValueError(f"Invalid log level: {level}")

    stage = os.getenv("STAGE", "DEV").upper()

    log_dir = "/var/log" if not location else location
    if stage in ("PROD", "STAGING"):
        os.makedirs(log_dir, exist_ok=True)

    handlers: dict[str, dict] = {}
    root_handlers: list[str] = []

    if stage in ("DEV", "STAGING"):
        handlers["stdout"] = {
            "level": level,
            "formatter": "json",
            "class": "logging.StreamHandler",
        }
        root_handlers.append("stdout")

    if stage in ("PROD", "STAGING"):
        # Root logger writes to service.log (generic)
        handlers["file"] = {
            "level": level,
            "formatter": "json",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": f"{log_dir}/{service}.log",
            "mode": "a",
            "maxBytes": max_bytes,
            "backupCount": backup_count,
            "encoding": "utf-8",
        }
        root_handlers.append("file")

    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {"json": {"()": DatadogJSONFormatter}},
        "handlers": handlers,
        "root": {"handlers": root_handlers, "level": level},
    }

    logging.config.dictConfig(logging_config)

    # Add global dd.* fields
    root_logger = logging.getLogger()
    adapter = logging.LoggerAdapter(
        root_logger,
        extra={
            "dd.service": service,
            "dd.env": env,
            "dd.version": version,
        },
    )

    _dd_log_configured = True
    #   _dd_log_configured = True
    _dd_log = adapter

    return adapter


# TODO - DEPRECATED
def setup_logging(name: str | int, level: str, location: str | None = None) -> bool:
    """
    Configured by the following environment variables:
    KAYA_LOG_NAME
    KAYA_LOG_LVL
    KAYA_LOG_DIR
    KAYA_LOG_FMT
    """
    if not isinstance(name, str) or level not in (
        "CRITICAL",
        "ERROR",
        "WARNING",
        "INFO",
        "DEBUG",
        "NOTSET",
    ):
        return False
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": os.getenv("KAYA_LOG_FMT", "%(asctime)s [%(levelname)s] %(name)s: %(message)s"),
            },
        },
        "handlers": {
            "default": {
                "level": level,
                "formatter": "standard",
                "class": "logging.StreamHandler",
            },
            "file": {
                "level": level,
                "formatter": "standard",
                "class": "logging.FileHandler",
                "filename": ("/var/log" if not location else location) + f"/{name}.log",
                "mode": "a",
            },
        },
        "loggers": {
            name: {"handlers": ["default", "file"], "level": level, "propagate": True},
        },
    }

    logging.config.dictConfig(logging_config)
    return True


# CODE DUMP
