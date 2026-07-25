from __future__ import annotations

from flask import Blueprint, render_template

bp = Blueprint("admissions", __name__, url_prefix="/admissions")


@bp.get("/")
def index():
    return render_template("pages/placeholder.html", title="Tuyển sinh", message="Module tuyển sinh sẽ kế thừa quy trình tiếp nhận hồ sơ, xét tuyển và nhập học.")
