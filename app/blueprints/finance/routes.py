from __future__ import annotations

from flask import Blueprint, render_template

bp = Blueprint("finance", __name__, url_prefix="/finance")


@bp.get("/")
def index():
    return render_template("pages/placeholder.html", title="Tài chính", message="Module tài chính sẽ quản lý hóa đơn, thanh toán, công nợ và học bổng.")
