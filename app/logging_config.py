from __future__ import annotations

import logging
from logging.config import dictConfig

from flask import Flask


def configure_logging(app: Flask) -> None:
    log_level = app.config.get("LOG_LEVEL", "INFO")

    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                }
            },
            "root": {
                "level": log_level,
                "handlers": ["console"],
            },
        }
    )
    app.logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
