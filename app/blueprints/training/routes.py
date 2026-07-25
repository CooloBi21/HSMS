from __future__ import annotations

from flask import Blueprint, render_template

from app.security import permission_required

bp = Blueprint("training", __name__, url_prefix="/training")


@bp.get("/")
@permission_required("training:access")
def index():
    return render_template("pages/placeholder.html", title="Đào tạo", message="Module đào tạo sẽ quản lý chương trình, học phần, thời khóa biểu và chuyên cần.")


@bp.get("/assigned")
@permission_required("training:assigned:view")
def assigned():
    return render_template("pages/placeholder.html", title="Lịch giảng dạy", message="Giáo viên xem lịch và học phần được phân công.")


@bp.get("/my-schedule")
@permission_required("schedule:self:view")
def my_schedule():
    return render_template("pages/placeholder.html", title="Lịch học", message="Học sinh xem lịch học của chính mình.")
