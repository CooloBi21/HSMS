from __future__ import annotations

from flask import Blueprint, render_template

from app.security import permission_required

bp = Blueprint("teachers", __name__, url_prefix="/teachers")


@bp.get("/")
@permission_required("teachers:manage")
def index():
    return render_template("pages/placeholder.html", title="Giáo viên", message="Module giáo viên sẽ được triển khai web sau khi hoàn tất nền Flask.")
