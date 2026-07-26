from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user

from app.security import permission_required
from app.repositories.mvp_repository import SchoolClassRepository
from app.services.mvp_service import SchoolClassService, ValidationError

bp = Blueprint("classes", __name__, url_prefix="/classes")


@bp.get("/")
@permission_required("classes:manage")
def index():
    grade_level = request.args.get("grade_level", "")
    return render_template(
        "classes/index.html",
        classes=SchoolClassService.list(grade_level or None),
        grades=SchoolClassRepository.grades(),
        selected_grade=grade_level,
    )


@bp.route("/new", methods=["GET", "POST"])
@permission_required("classes:manage")
def create():
    return _save_class()


@bp.route("/<int:class_id>/edit", methods=["GET", "POST"])
@permission_required("classes:manage")
def edit(class_id: int):
    school_class = SchoolClassRepository.get(class_id)
    if not school_class:
        flash("Không tìm thấy lớp học.", "danger")
        return redirect(url_for("classes.index"))
    return _save_class(school_class)


@bp.post("/<int:class_id>/delete")
@permission_required("classes:manage")
def delete(class_id: int):
    try:
        SchoolClassService.delete(class_id, current_user)
        flash("Đã xóa lớp học.", "success")
    except ValidationError as exc:
        flash(str(exc), "danger")
    return redirect(url_for("classes.index"))


@bp.get("/assigned")
@permission_required("teacher:assigned:view")
def assigned():
    return render_template("pages/placeholder.html", title="Lớp được phân công", message="Giáo viên chỉ xem các lớp nằm trong phạm vi được giao.")


@bp.get("/my")
@permission_required("classes:self:view")
def my_class():
    return render_template("pages/placeholder.html", title="Lớp của tôi", message="Học sinh chỉ xem lớp của chính mình.")


def _save_class(school_class=None):
    if request.method == "POST":
        try:
            SchoolClassService.save(request.form, current_user, school_class.id if school_class else None)
            flash("Đã lưu lớp học.", "success")
            return redirect(url_for("classes.index"))
        except ValidationError as exc:
            flash(str(exc), "danger")
    return render_template("classes/form.html", school_class=school_class)
