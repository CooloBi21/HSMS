from __future__ import annotations

from flask import Blueprint, render_template

bp = Blueprint("students", __name__, url_prefix="/students")


@bp.get("/")
def index():
    return render_template("pages/placeholder.html", title="Học sinh", message="Module học sinh sẽ kế thừa nghiệp vụ từ desktop ở giai đoạn chuyển đổi tiếp theo.")
