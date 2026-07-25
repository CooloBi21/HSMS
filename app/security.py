from __future__ import annotations

from functools import wraps
from typing import Callable, TypeVar

from flask import abort
from flask_login import current_user, login_required

from app.services.auth_service import AuthService

F = TypeVar("F", bound=Callable)


def permission_required(permission: str):
    def decorator(func: F) -> F:
        @wraps(func)
        @login_required
        def wrapper(*args, **kwargs):  # type: ignore[no-untyped-def]
            if not AuthService.has_permission(current_user, permission):
                abort(403)
            return func(*args, **kwargs)

        return wrapper  # type: ignore[return-value]

    return decorator


def role_required(*roles: str):
    def decorator(func: F) -> F:
        @wraps(func)
        @login_required
        def wrapper(*args, **kwargs):  # type: ignore[no-untyped-def]
            if not current_user.is_authenticated or current_user.role not in roles:
                abort(403)
            return func(*args, **kwargs)

        return wrapper  # type: ignore[return-value]

    return decorator
