from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user

from app.repositories.mvp_repository import SchoolClassRepository
from app.repositories.profile_repository import StudentProfileRepository
from app.security import permission_required
from app.services.mvp_service import ValidationError
from app.services.profile_service import LEARNING_STATUSES, POLICY_TYPES, StudentProfileService

bp = Blueprint("profiles", __name__, url_prefix="/profiles")


@bp.get("/")
@permission_required("profiles:access")
def index():
    search = request.args.get("q", "")
    status = request.args.get("status", "")
    policy_type = request.args.get("policy_type", "")
    return render_template(
        "profiles/index.html",
        profiles=StudentProfileService.list(search, status or None, policy_type or None),
        search=search,
        selected_status=status,
        selected_policy=policy_type,
        statuses=sorted(LEARNING_STATUSES),
        policies=sorted(policy for policy in POLICY_TYPES if policy),
    )


@bp.route("/<int:student_id>/edit", methods=["GET", "POST"])
@permission_required("profiles:access")
def edit(student_id: int):
    try:
        student = StudentProfileService.get(student_id)
    except ValidationError as exc:
        flash(str(exc), "danger")
        return redirect(url_for("profiles.index"))
    if request.method == "POST":
        try:
            StudentProfileService.update_profile(student_id, request.form, current_user)
            flash("Đã cập nhật hồ sơ học sinh.", "success")
            return redirect(url_for("profiles.index"))
        except ValidationError as exc:
            flash(str(exc), "danger")
    return render_template(
        "profiles/form.html",
        student=student,
        classes=SchoolClassRepository.list(),
        statuses=sorted(LEARNING_STATUSES),
        policies=sorted(policy for policy in POLICY_TYPES if policy),
    )


@bp.get("/me")
@permission_required("profile:self:view")
def me():
    try:
        student = StudentProfileService.get_self_profile(current_user)
    except ValidationError as exc:
        flash(str(exc), "danger")
        return redirect(url_for("auth.login"))
    return render_template("profiles/detail.html", student=student)
