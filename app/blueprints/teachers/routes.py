from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user

from app.security import permission_required
from app.repositories.mvp_repository import TeacherRepository
from app.services.mvp_service import TeacherService, ValidationError

bp = Blueprint("teachers", __name__, url_prefix="/teachers")


@bp.get("/")
@permission_required("teachers:manage")
def index():
    status = request.args.get("status", "")
    return render_template(
        "teachers/index.html",
        teachers=TeacherService.list(status or None),
        statuses=TeacherRepository.statuses(),
        selected_status=status,
    )


@bp.route("/new", methods=["GET", "POST"])
@permission_required("teachers:manage")
def create():
    return _save_teacher()


@bp.route("/<int:teacher_id>/edit", methods=["GET", "POST"])
@permission_required("teachers:manage")
def edit(teacher_id: int):
    teacher = TeacherRepository.get(teacher_id)
    if not teacher:
        flash("Không tìm thấy giáo viên.", "danger")
        return redirect(url_for("teachers.index"))
    return _save_teacher(teacher)


@bp.post("/<int:teacher_id>/delete")
@permission_required("teachers:manage")
def delete(teacher_id: int):
    try:
        TeacherService.delete(teacher_id, current_user)
        flash("Đã xóa giáo viên.", "success")
    except ValidationError as exc:
        flash(str(exc), "danger")
    return redirect(url_for("teachers.index"))


def _save_teacher(teacher=None):
    if request.method == "POST":
        try:
            TeacherService.save(request.form, current_user, teacher.id if teacher else None)
            flash("Đã lưu giáo viên.", "success")
            return redirect(url_for("teachers.index"))
        except ValidationError as exc:
            flash(str(exc), "danger")
    return render_template("teachers/form.html", teacher=teacher)
