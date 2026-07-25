from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app.blueprints.auth.forms import ChangePasswordForm, LoginForm
from app.repositories.auth_repository import ActivityLogRepository
from app.security import permission_required
from app.services.auth_service import AuthService, AuthenticationError

bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    form = LoginForm()
    if form.validate_on_submit():
        try:
            user = AuthService.authenticate(form.username.data, form.password.data)
            login_user(user)
            next_url = request.args.get("next")
            return redirect(next_url or url_for(AuthService.default_endpoint(user)))
        except AuthenticationError as exc:
            flash(str(exc), "danger")

    return render_template("auth/login.html", form=form)


@bp.post("/logout")
@login_required
def logout():
    AuthService.log_activity(current_user, "logout", "auth", detail="Đăng xuất hệ thống")
    logout_user()
    flash("Đã đăng xuất.", "success")
    return redirect(url_for("auth.login"))


@bp.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        try:
            AuthService.change_password(current_user, form.current_password.data, form.new_password.data)
            flash("Đổi mật khẩu thành công.", "success")
            return redirect(url_for("dashboard.index"))
        except (AuthenticationError, ValueError) as exc:
            flash(str(exc), "danger")

    return render_template("auth/change_password.html", form=form)


@bp.get("/activity-log")
@permission_required("activity:view")
def activity_log():
    logs = ActivityLogRepository.latest()
    return render_template("auth/activity_log.html", logs=logs)
