from __future__ import annotations

from flask import Blueprint, render_template

from app.security import permission_required
from app.services.operations_overview_service import TrainingOverviewService

bp = Blueprint("training", __name__, url_prefix="/training")


@bp.get("/")
@permission_required("training:access")
def index():
    return render_template("training/index.html", data=TrainingOverviewService.overview())


@bp.get("/assigned")
@permission_required("training:assigned:view")
def assigned():
    return render_template("pages/placeholder.html", title="Lịch giảng dạy", message="Giáo viên xem lịch và học phần được phân công.")


@bp.get("/my-schedule")
@permission_required("schedule:self:view")
def my_schedule():
    return render_template("pages/placeholder.html", title="Lịch học", message="Học sinh xem lịch học của chính mình.")
