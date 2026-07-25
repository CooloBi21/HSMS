from __future__ import annotations

from flask import Blueprint, render_template

bp = Blueprint("classes", __name__, url_prefix="/classes")


@bp.get("/")
def index():
    return render_template("pages/placeholder.html", title="Lớp học", message="Module lớp học sẽ được chuyển từ service/DAO desktop sang web.")
