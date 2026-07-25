from __future__ import annotations

from flask import Blueprint, render_template

from app.security import permission_required

bp = Blueprint("students", __name__, url_prefix="/students")


@bp.get("/")
@permission_required("students:manage")
def index():
    return render_template("pages/placeholder.html", title="Học sinh", message="Module học sinh sẽ kế thừa nghiệp vụ từ desktop ở giai đoạn chuyển đổi tiếp theo.")


@bp.get("/me")
@permission_required("student:self:view")
def me():
    return render_template("pages/placeholder.html", title="Hồ sơ của tôi", message="Học sinh chỉ xem hồ sơ gắn với tài khoản của chính mình.")
