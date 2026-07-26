from __future__ import annotations

from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
csrf = CSRFProtect()

login_manager.login_view = "auth.login"
login_manager.login_message = "Vui lòng đăng nhập để tiếp tục."


@login_manager.user_loader
def load_user(user_id: str):  # type: ignore[no-untyped-def]
    """Resolve logged-in users from the web account table."""

    from app.repositories.auth_repository import UserRepository

    return UserRepository.get_by_id(user_id)
