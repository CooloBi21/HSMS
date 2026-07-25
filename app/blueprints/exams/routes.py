from __future__ import annotations

from flask import Blueprint, render_template

bp = Blueprint("exams", __name__, url_prefix="/exams")


@bp.get("/")
def index():
    return render_template("pages/placeholder.html", title="Khảo thí", message="Module khảo thí sẽ quản lý lịch thi, điểm, GPA, điều kiện thi và phúc khảo.")
