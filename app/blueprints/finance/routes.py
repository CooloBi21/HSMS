from __future__ import annotations

from flask import Blueprint, render_template

from app.security import permission_required

bp = Blueprint("finance", __name__, url_prefix="/finance")


@bp.get("/")
@permission_required("finance:access")
def index():
    return render_template("pages/placeholder.html", title="Tài chính", message="Module tài chính sẽ quản lý hóa đơn, thanh toán, công nợ và học bổng.")
