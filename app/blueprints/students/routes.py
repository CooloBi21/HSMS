from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user

from app.security import permission_required
from app.repositories.mvp_repository import SchoolClassRepository, StudentRepository
from app.services.mvp_service import StudentService, ValidationError

bp = Blueprint("students", __name__, url_prefix="/students")


@bp.get("/")
@permission_required("students:manage")
def index():
    page = max(request.args.get("page", 1, type=int), 1)
    class_id = request.args.get("class_id", type=int)
    search = request.args.get("q", "")
    pagination = StudentService.list(search, class_id, page)
    return render_template(
        "students/index.html",
        pagination=pagination,
        classes=SchoolClassRepository.list(),
        selected_class_id=class_id,
        search=search,
    )


@bp.route("/new", methods=["GET", "POST"])
@permission_required("students:manage")
def create():
    return _save_student()


@bp.route("/<int:student_id>/edit", methods=["GET", "POST"])
@permission_required("students:manage")
def edit(student_id: int):
    student = StudentRepository.get(student_id)
    if not student:
        flash("Không tìm thấy học sinh.", "danger")
        return redirect(url_for("students.index"))
    return _save_student(student)


@bp.post("/<int:student_id>/delete")
@permission_required("students:manage")
def delete(student_id: int):
    try:
        StudentService.delete(student_id, current_user)
        flash("Đã xóa học sinh.", "success")
    except ValidationError as exc:
        flash(str(exc), "danger")
    return redirect(url_for("students.index"))


@bp.get("/me")
@permission_required("student:self:view")
def me():
    return render_template("pages/placeholder.html", title="Hồ sơ của tôi", message="Học sinh chỉ xem hồ sơ gắn với tài khoản của chính mình.")


def _save_student(student=None):
    if request.method == "POST":
        try:
            StudentService.save(request.form, current_user, student.id if student else None)
            flash("Đã lưu học sinh.", "success")
            return redirect(url_for("students.index"))
        except ValidationError as exc:
            flash(str(exc), "danger")
    return render_template("students/form.html", student=student, classes=SchoolClassRepository.list())
