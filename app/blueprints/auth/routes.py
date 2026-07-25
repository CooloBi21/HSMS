from __future__ import annotations

from flask import Blueprint, render_template

bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.get("/login")
def login():
    return render_template("pages/placeholder.html", title="Đăng nhập", message="Màn hình đăng nhập sẽ được triển khai ở giai đoạn chuyển nghiệp vụ tài khoản.")
