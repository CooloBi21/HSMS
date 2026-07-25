from __future__ import annotations

from flask import Blueprint, render_template

bp = Blueprint("affairs", __name__, url_prefix="/affairs")


@bp.get("/")
def index():
    return render_template("pages/placeholder.html", title="Công tác sinh viên", message="Module công tác sinh viên sẽ quản lý rèn luyện, ký túc xá, ngoại khóa và y tế.")
