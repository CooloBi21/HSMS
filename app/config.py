from __future__ import annotations

import os
from dataclasses import dataclass


def _bool_from_env(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass
class BaseConfig:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-change-me")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///hsms_web_dev.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = _bool_from_env("WTF_CSRF_ENABLED", True)
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    APP_NAME = "HSMS Web"


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    ENV_NAME = "development"


class TestingConfig(BaseConfig):
    TESTING = True
    WTF_CSRF_ENABLED = False
    ENV_NAME = "testing"
    SQLALCHEMY_DATABASE_URI = os.getenv("TEST_DATABASE_URL", "sqlite:///:memory:")


class ProductionConfig(BaseConfig):
    DEBUG = False
    ENV_NAME = "production"


CONFIG_MAP = {
    "development": DevelopmentConfig,
    "dev": DevelopmentConfig,
    "testing": TestingConfig,
    "test": TestingConfig,
    "production": ProductionConfig,
    "prod": ProductionConfig,
}


def get_config(config_name: str | None = None) -> type[BaseConfig]:
    selected = config_name or os.getenv("HSMS_ENV") or os.getenv("FLASK_ENV") or "development"
    return CONFIG_MAP.get(selected.lower(), DevelopmentConfig)
