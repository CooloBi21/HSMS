from __future__ import annotations

from flask import Flask


def register_commands(app: Flask) -> None:
    @app.cli.command("health")
    def health() -> None:
        """Print a simple health status for deployment checks."""

        print("HSMS Web is healthy")
