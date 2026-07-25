from __future__ import annotations

from flask import Blueprint, render_template

from app.security import permission_required

bp = Blueprint("affairs", __name__, url_prefix="/affairs")


@bp.get("/")
@permission_required("affairs:access")
def index():
    return render_template("pages/placeholder.html", title="Công tác sinh viên", message="Module công tác sinh viên sẽ quản lý rèn luyện, ký túc xá, ngoại khóa và y tế.")
