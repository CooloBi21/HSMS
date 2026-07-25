from __future__ import annotations

import hashlib

import pytest

from app import create_app
from app.extensions import db
from app.models.auth import AccountStatus, Role, User
from app.services.auth_service import AuthService, AuthorizationError


@pytest.fixture()
def app_context():
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        admin = AuthService.create_user("admin", "Admin", "Admin123", Role.ADMIN)
        student = AuthService.create_user(
            "student",
            "Student",
            "Student123",
            Role.STUDENT,
            student_code="S0001",
        )
        teacher = AuthService.create_user(
            "teacher",
            "Teacher",
            "Teacher123",
            Role.TEACHER,
            teacher_code="T0001",
        )
        locked = AuthService.create_user(
            "locked",
            "Locked",
            "Locked123",
            Role.STUDENT,
            status=AccountStatus.LOCKED,
        )
        yield app, admin, student, teacher, locked
        db.session.remove()
        db.drop_all()


def login(client, username: str, password: str):
    return client.post("/auth/login", data={"username": username, "password": password}, follow_redirects=False)


def test_password_is_hashed(app_context) -> None:
    app, admin, *_ = app_context
    with app.app_context():
        stored = db.session.get(User, admin.id).password_hash

    assert stored != "Admin123"
    assert stored != hashlib.sha256("Admin123".encode()).hexdigest()
    assert len(stored) > 40


def test_login_logout_and_activity_log(app_context) -> None:
    app, *_ = app_context
    client = app.test_client()

    response = login(client, "admin", "Admin123")

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/")

    activity_response = client.get("/auth/activity-log")
    assert activity_response.status_code == 200
    assert "login" in activity_response.get_data(as_text=True)

    logout_response = client.post("/auth/logout")
    assert logout_response.status_code == 302


def test_locked_account_cannot_login(app_context) -> None:
    app, *_ = app_context
    client = app.test_client()

    response = login(client, "locked", "Locked123")

    assert response.status_code == 200
    assert "Tài khoản không ở trạng thái hoạt động." in response.get_data(as_text=True)


def test_sensitive_routes_check_server_permission(app_context) -> None:
    app, *_ = app_context
    client = app.test_client()

    unauthenticated = client.get("/students/")
    assert unauthenticated.status_code == 302
    assert "/auth/login" in unauthenticated.headers["Location"]

    login(client, "student", "Student123")
    forbidden = client.get("/students/")
    assert forbidden.status_code == 403


def test_admin_can_access_management_routes(app_context) -> None:
    app, *_ = app_context
    client = app.test_client()

    login(client, "admin", "Admin123")
    response = client.get("/students/")

    assert response.status_code == 200


def test_teacher_and_student_scope_routes(app_context) -> None:
    app, *_ = app_context
    client = app.test_client()

    login(client, "teacher", "Teacher123")
    assert client.get("/classes/assigned").status_code == 200
    assert client.get("/classes/").status_code == 403

    client.post("/auth/logout")
    login(client, "student", "Student123")
    assert client.get("/students/me").status_code == 200
    assert client.get("/classes/assigned").status_code == 403


def test_non_admin_cannot_change_role(app_context) -> None:
    app, admin, student, *_ = app_context
    with app.app_context():
        with pytest.raises(AuthorizationError):
            AuthService.update_role(admin, Role.STUDENT, student)


def test_service_scope_checks(app_context) -> None:
    app, admin, student, teacher, *_ = app_context
    with app.app_context():
        AuthService.ensure_student_scope(admin, "S9999")
        AuthService.ensure_student_scope(student, "S0001")
        AuthService.ensure_teacher_scope(teacher, "T0001")

        with pytest.raises(AuthorizationError):
            AuthService.ensure_student_scope(student, "S0002")

        with pytest.raises(AuthorizationError):
            AuthService.ensure_teacher_scope(teacher, "T0002")


def test_seed_admin_cli_creates_admin() -> None:
    app = create_app("testing")
    runner = app.test_cli_runner()

    with app.app_context():
        result = runner.invoke(
            args=[
                "seed-admin",
                "--username",
                "seeded-admin",
                "--password",
                "Seeded123",
                "--full-name",
                "Seeded Admin",
            ]
        )
        user = User.query.filter_by(username="seeded-admin").first()
        db.session.remove()
        db.drop_all()

    assert result.exit_code == 0
    assert user is not None
    assert user.role == Role.ADMIN.value
