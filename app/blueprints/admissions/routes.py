from __future__ import annotations

from flask import Blueprint, render_template

from app.security import permission_required

bp = Blueprint("admissions", __name__, url_prefix="/admissions")


@bp.get("/")
@permission_required("admissions:access")
def index():
    return render_template("pages/placeholder.html", title="Tuyển sinh", message="Module tuyển sinh sẽ kế thừa quy trình tiếp nhận hồ sơ, xét tuyển và nhập học.")
