from __future__ import annotations

from flask import Blueprint, render_template

bp = Blueprint("training", __name__, url_prefix="/training")


@bp.get("/")
def index():
    return render_template("pages/placeholder.html", title="Đào tạo", message="Module đào tạo sẽ quản lý chương trình, học phần, thời khóa biểu và chuyên cần.")
