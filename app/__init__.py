from __future__ import annotations

from importlib import import_module

from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

from app.commands import register_commands
from app.config import get_config
from app.extensions import csrf, db, login_manager, migrate
from app.logging_config import configure_logging


def create_app(config_name: str | None = None) -> Flask:
    """Create and configure the HSMS Flask application."""

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(get_config(config_name))
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)
    import_module("app.models")

    configure_logging(app)
    init_extensions(app)
    register_blueprints(app)
    register_error_handlers(app)
    register_commands(app)

    return app


def init_extensions(app: Flask) -> None:
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)


def register_blueprints(app: Flask) -> None:
    from app.blueprints.admissions.routes import bp as admissions_bp
    from app.blueprints.affairs.routes import bp as affairs_bp
    from app.blueprints.auth.routes import bp as auth_bp
    from app.blueprints.classes.routes import bp as classes_bp
    from app.blueprints.dashboard.routes import bp as dashboard_bp
    from app.blueprints.exams.routes import bp as exams_bp
    from app.blueprints.finance.routes import bp as finance_bp
    from app.blueprints.graduation.routes import bp as graduation_bp
    from app.blueprints.profiles.routes import bp as profiles_bp
    from app.blueprints.students.routes import bp as students_bp
    from app.blueprints.teachers.routes import bp as teachers_bp
    from app.blueprints.training.routes import bp as training_bp

    app.register_blueprint(dashboard_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(students_bp)
    app.register_blueprint(classes_bp)
    app.register_blueprint(teachers_bp)
    app.register_blueprint(admissions_bp)
    app.register_blueprint(profiles_bp)
    app.register_blueprint(training_bp)
    app.register_blueprint(exams_bp)
    app.register_blueprint(finance_bp)
    app.register_blueprint(affairs_bp)
    app.register_blueprint(graduation_bp)


def register_error_handlers(app: Flask) -> None:
    from app.blueprints.errors.handlers import register_error_handlers as register_handlers

    register_handlers(app)
