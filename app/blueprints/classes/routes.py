from __future__ import annotations

from flask import Blueprint, render_template

from app.security import permission_required

bp = Blueprint("classes", __name__, url_prefix="/classes")


@bp.get("/")
@permission_required("classes:manage")
def index():
    return render_template("pages/placeholder.html", title="Lớp học", message="Module lớp học sẽ được chuyển từ service/DAO desktop sang web.")


@bp.get("/assigned")
@permission_required("teacher:assigned:view")
def assigned():
    return render_template("pages/placeholder.html", title="Lớp được phân công", message="Giáo viên chỉ xem các lớp nằm trong phạm vi được giao.")


@bp.get("/my")
@permission_required("classes:self:view")
def my_class():
    return render_template("pages/placeholder.html", title="Lớp của tôi", message="Học sinh chỉ xem lớp của chính mình.")
