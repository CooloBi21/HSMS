from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user

from app.repositories.admission_repository import AdmissionRepository
from app.repositories.mvp_repository import SchoolClassRepository
from app.security import permission_required
from app.services.admission_web_service import AdmissionWebService
from app.services.mvp_service import ValidationError

bp = Blueprint("admissions", __name__, url_prefix="/admissions")


@bp.get("/")
@permission_required("admissions:access")
def index():
    search = request.args.get("q", "")
    status = request.args.get("status", "")
    return render_template(
        "admissions/index.html",
        applications=AdmissionWebService.list(search, status or None),
        search=search,
        selected_status=status,
    )


@bp.route("/new", methods=["GET", "POST"])
@permission_required("admissions:access")
def create():
    return _save_application()


@bp.route("/<int:application_id>/edit", methods=["GET", "POST"])
@permission_required("admissions:access")
def edit(application_id: int):
    application = AdmissionRepository.get(application_id)
    if not application:
        flash("Không tìm thấy hồ sơ tuyển sinh.", "danger")
        return redirect(url_for("admissions.index"))
    return _save_application(application)


@bp.post("/<int:application_id>/screen")
@permission_required("admissions:access")
def screen(application_id: int):
    try:
        AdmissionWebService.auto_screen(application_id, current_user)
        flash("Đã xét tuyển hồ sơ.", "success")
    except ValidationError as exc:
        flash(str(exc), "danger")
    return redirect(url_for("admissions.index"))


@bp.post("/<int:application_id>/enroll")
@permission_required("admissions:access")
def enroll(application_id: int):
    try:
        student_code = AdmissionWebService.enroll(application_id, current_user)
        flash(f"Đã nhập học và cấp mã học sinh {student_code}.", "success")
    except ValidationError as exc:
        flash(str(exc), "danger")
    return redirect(url_for("admissions.index"))


@bp.post("/<int:application_id>/delete")
@permission_required("admissions:access")
def delete(application_id: int):
    try:
        AdmissionWebService.delete(application_id, current_user)
        flash("Đã xóa hồ sơ tuyển sinh.", "success")
    except ValidationError as exc:
        flash(str(exc), "danger")
    return redirect(url_for("admissions.index"))


def _save_application(application=None):
    if request.method == "POST":
        try:
            AdmissionWebService.receive_application(request.form, current_user, application.id if application else None)
            flash("Đã lưu hồ sơ tuyển sinh.", "success")
            return redirect(url_for("admissions.index"))
        except ValidationError as exc:
            flash(str(exc), "danger")
    return render_template("admissions/form.html", application=application, classes=SchoolClassRepository.list())
