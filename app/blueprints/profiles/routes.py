from __future__ import annotations

from flask import Blueprint, render_template

bp = Blueprint("profiles", __name__, url_prefix="/profiles")


@bp.get("/")
def index():
    return render_template("pages/placeholder.html", title="Hồ sơ cá nhân", message="Module hồ sơ sẽ quản lý lý lịch, trạng thái, chính sách, khen thưởng và kỷ luật.")
