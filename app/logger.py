"""Rich-based logging configuration with unified styling for app and uvicorn."""

from __future__ import annotations

import logging
import logging.config
import os
from typing import Any, Dict


def build_log_config(level: str = "INFO", time_format: str = "[%H:%M:%S]") -> Dict[str, Any]:
    """Return a dictConfig using rich.logging.RichHandler.

    - Colors, levels, time, and path handled by RichHandler
    - Shared handler for root and uvicorn loggers
    """
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            # RichHandler renders level, time, and path; formatter keeps message only
            "rich": {
                "format": "%(message)s",
            }
        },
        "handlers": {
            "console": {
                "class": "rich.logging.RichHandler",
                "level": level,
                "formatter": "rich",
                "rich_tracebacks": True,
                "show_time": True,
                "omit_repeated_times": True,
                "show_level": True,
                "show_path": True,
                "enable_link_path": True,
                "markup": False,
                "log_time_format": time_format,
            }
        },
        "loggers": {
            # Root logger for application
            "": {
                "handlers": ["console"],
                "level": level,
                "propagate": False,
            },
            # Uvicorn family
            "uvicorn": {
                "handlers": ["console"],
                "level": "INFO",
                "propagate": False,
            },
            "uvicorn.error": {
                "handlers": ["console"],
                "level": "INFO",
                "propagate": False,
            },
            "uvicorn.access": {
                "handlers": ["console"],
                "level": "INFO",
                "propagate": False,
            },
        },
    }


_DEFAULT_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
_TIME_FORMAT = os.getenv("LOG_TIME_FORMAT", "[%H:%M:%S]")

# Public uvicorn-ready configuration
UVICORN_LOG_CONFIG = build_log_config(level=_DEFAULT_LEVEL, time_format=_TIME_FORMAT)

# Configure logging at import for application modules using `from app.logger import logger`
logging.config.dictConfig(UVICORN_LOG_CONFIG)
logger = logging.getLogger("app")
