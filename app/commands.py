from __future__ import annotations

import os

import click
from flask import Flask

from app.extensions import db
from app.services.auth_service import create_initial_admin


def register_commands(app: Flask) -> None:
    @app.cli.command("health")
    def health() -> None:
        """Print a simple health status for deployment checks."""

        print("HSMS Web is healthy")

    @app.cli.command("init-db")
    def init_db() -> None:
        """Create database tables for the current environment."""

        db.create_all()
        click.echo("Database tables created.")

    @app.cli.command("seed-admin")
    @click.option("--username", default=None, help="Admin username. Defaults to ADMIN_USERNAME env.")
    @click.option("--password", default=None, help="Admin password. Defaults to ADMIN_PASSWORD env.")
    @click.option("--full-name", default=None, help="Admin display name. Defaults to ADMIN_FULL_NAME env.")
    def seed_admin(username: str | None, password: str | None, full_name: str | None) -> None:
        """Seed the first admin account from env variables or CLI arguments."""

        admin_username = username or os.getenv("ADMIN_USERNAME")
        admin_password = password or os.getenv("ADMIN_PASSWORD")
        admin_full_name = full_name or os.getenv("ADMIN_FULL_NAME") or "System Admin"

        if not admin_username or not admin_password:
            raise click.ClickException("Provide ADMIN_USERNAME and ADMIN_PASSWORD or pass --username/--password.")

        db.create_all()
        user = create_initial_admin(admin_username, admin_password, admin_full_name)
        click.echo(f"Admin account ready: {user.username}")
