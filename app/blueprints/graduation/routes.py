from __future__ import annotations

from flask import Blueprint, render_template

bp = Blueprint("graduation", __name__, url_prefix="/graduation")


@bp.get("/")
def index():
    return render_template("pages/placeholder.html", title="Tốt nghiệp", message="Module tốt nghiệp sẽ quản lý xét tốt nghiệp, văn bằng, biểu mẫu và cựu sinh viên.")
