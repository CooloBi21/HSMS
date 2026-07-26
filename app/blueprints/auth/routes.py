from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app.blueprints.auth.forms import ChangePasswordForm, LoginForm
from app.repositories.auth_repository import ActivityLogRepository
from app.security import permission_required
from app.services.auth_service import AuthService, AuthenticationError
from app.services.mvp_service import AccountService, ValidationError

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


@bp.route("/accounts", methods=["GET", "POST"])
@permission_required("accounts:manage")
def accounts():
    if request.method == "POST":
        try:
            AccountService.save(request.form, current_user)
            flash("Đã tạo tài khoản.", "success")
            return redirect(url_for("auth.accounts"))
        except (ValidationError, ValueError) as exc:
            flash(str(exc), "danger")
    return render_template("auth/accounts.html", accounts=AccountService.list())


@bp.post("/accounts/<int:user_id>/status")
@permission_required("accounts:manage")
def update_account_status(user_id: int):
    try:
        AccountService.update_status(user_id, request.form.get("status", ""), current_user)
        flash("Đã cập nhật trạng thái tài khoản.", "success")
    except (ValidationError, ValueError) as exc:
        flash(str(exc), "danger")
    return redirect(url_for("auth.accounts"))
