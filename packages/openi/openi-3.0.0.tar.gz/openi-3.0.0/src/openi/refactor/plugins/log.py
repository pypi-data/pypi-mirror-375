import logging
import logging.config
import os
from logging.handlers import TimedRotatingFileHandler
from typing import Literal

from openi.refactor.constants import LOG_FILE, LOG_LEVEL


def setup_logging() -> None:
    """Setup logging configuration based on environment variable."""
    log_path = LOG_FILE
    log_level = LOG_LEVEL

    os.makedirs(os.path.dirname(log_path), exist_ok=True)

    log_file = log_path
    log_level = log_level.upper()
    log_backup_count = 7  # Keep logs for the past 7 days

    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s - %(name)s(%(lineno)d) [%(levelname)s] %(message)s",
            },
        },
        "handlers": {
            "file": {
                "level": log_level,
                "class": "logging.handlers.TimedRotatingFileHandler",
                "filename": log_file,
                "when": "midnight",  # Rotate logs at midnight every day
                "backupCount": log_backup_count,  # Keep the last 7 days of logs
                "formatter": "default",
                "encoding": "utf-8",  # Set encoding to handle non-ASCII characters
            },
        },
        "root": {
            "level": log_level,
            "handlers": ["file"],
        },
    }

    logging.config.dictConfig(logging_config)
    logging.info(f"Logging initialized with level: {log_level}")
