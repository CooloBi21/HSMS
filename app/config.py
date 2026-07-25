from __future__ import annotations

import os
import secrets
from dataclasses import dataclass


def _bool_from_env(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass
class BaseConfig:
    APP_ENV = os.getenv("APP_ENV") or os.getenv("HSMS_ENV") or os.getenv("FLASK_ENV") or "development"
    SECRET_KEY = os.getenv("SECRET_KEY") or secrets.token_urlsafe(32)
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///hsms_web_dev.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = _bool_from_env("WTF_CSRF_ENABLED", True)
    CLOUDFLARE_ACCESS_ENABLED = _bool_from_env("CLOUDFLARE_ACCESS_ENABLED", False)
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    APP_NAME = "HSMS Web"
    ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")


class DevelopmentConfig(BaseConfig):
    DEBUG = _bool_from_env("FLASK_DEBUG", True)
    ENV_NAME = "development"


class TestingConfig(BaseConfig):
    TESTING = True
    WTF_CSRF_ENABLED = False
    ENV_NAME = "testing"
    SQLALCHEMY_DATABASE_URI = os.getenv("TEST_DATABASE_URL", "sqlite:///:memory:")


class ProductionConfig(BaseConfig):
    DEBUG = _bool_from_env("FLASK_DEBUG", False)
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
    selected = config_name or os.getenv("APP_ENV") or os.getenv("HSMS_ENV") or os.getenv("FLASK_ENV") or "development"
    if selected.lower() in {"production", "prod"}:
        if not os.getenv("SECRET_KEY"):
            raise RuntimeError("SECRET_KEY is required in production.")
        if not os.getenv("DATABASE_URL"):
            raise RuntimeError("DATABASE_URL is required in production.")
    return CONFIG_MAP.get(selected.lower(), DevelopmentConfig)
