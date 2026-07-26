from __future__ import annotations

from flask import Blueprint, render_template

from app.security import permission_required
from app.services.operations_overview_service import ExamOverviewService

bp = Blueprint("exams", __name__, url_prefix="/exams")


@bp.get("/")
@permission_required("exams:access")
def index():
    return render_template("exams/index.html", data=ExamOverviewService.overview())


@bp.get("/assigned")
@permission_required("exams:assigned:view")
def assigned():
    return render_template("pages/placeholder.html", title="Nhập điểm được phân công", message="Giáo viên nhập điểm trong phạm vi lớp hoặc học phần được giao.")


@bp.get("/my-grades")
@permission_required("grades:self:view")
def my_grades():
    return render_template("pages/placeholder.html", title="Điểm của tôi", message="Học sinh chỉ xem điểm của chính mình.")
