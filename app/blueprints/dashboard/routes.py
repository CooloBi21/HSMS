from __future__ import annotations

from flask import Blueprint, current_app, jsonify, render_template

from app.security import permission_required
from app.services.mvp_service import DashboardService

bp = Blueprint("dashboard", __name__)


@bp.get("/")
@permission_required("dashboard:view")
def index():
    return render_template("dashboard/index.html", data=DashboardService.overview())


@bp.get("/health")
def healthcheck():
    return jsonify(
        {
            "status": "ok",
            "app": current_app.config["APP_NAME"],
            "environment": current_app.config["ENV_NAME"],
        }
    )
