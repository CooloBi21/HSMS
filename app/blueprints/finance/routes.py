from __future__ import annotations

from flask import Blueprint, render_template

from app.security import permission_required
from app.services.operations_overview_service import FinanceOverviewService

bp = Blueprint("finance", __name__, url_prefix="/finance")


@bp.get("/")
@permission_required("finance:access")
def index():
    return render_template("finance/index.html", data=FinanceOverviewService.overview())
