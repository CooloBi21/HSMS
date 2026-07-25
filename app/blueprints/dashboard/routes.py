from __future__ import annotations

from flask import Blueprint, current_app, jsonify, render_template

from app.security import permission_required

bp = Blueprint("dashboard", __name__)


@bp.get("/")
@permission_required("dashboard:view")
def index():
    modules = [
        ("Tuyển sinh", "admissions.index"),
        ("Học sinh", "students.index"),
        ("Lớp học", "classes.index"),
        ("Giáo viên", "teachers.index"),
        ("Hồ sơ", "profiles.index"),
        ("Đào tạo", "training.index"),
        ("Khảo thí", "exams.index"),
        ("Tài chính", "finance.index"),
        ("Công tác SV", "affairs.index"),
        ("Tốt nghiệp", "graduation.index"),
    ]
    return render_template("dashboard/index.html", modules=modules)


@bp.get("/health")
def healthcheck():
    return jsonify(
        {
            "status": "ok",
            "app": current_app.config["APP_NAME"],
            "environment": current_app.config["ENV_NAME"],
        }
    )
