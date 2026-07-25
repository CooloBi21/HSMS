from __future__ import annotations

import pytest

from app import create_app
from app.extensions import db
from app.models.academic import SchoolClass, Student
from app.models.auth import Role, User
from app.services.auth_service import AuthService


@pytest.fixture()
def mvp_app():
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        AuthService.create_user("admin", "Admin", "Admin123", Role.ADMIN)
        yield app
        db.session.remove()
        db.drop_all()


def login_admin(client):
    return client.post("/auth/login", data={"username": "admin", "password": "Admin123"})


def test_admin_dashboard_and_activity_log(mvp_app) -> None:
    client = mvp_app.test_client()
    login_admin(client)

    response = client.get("/")
    activity = client.get("/auth/activity-log")

    assert response.status_code == 200
    assert "Tổng quan hệ thống" in response.get_data(as_text=True)
    assert activity.status_code == 200
    assert "login" in activity.get_data(as_text=True)


def test_class_crud_and_prevent_delete_when_has_students(mvp_app) -> None:
    client = mvp_app.test_client()
    login_admin(client)

    create_response = client.post("/classes/new", data={"code": "C10A1", "name": "Lớp 10A1", "grade_level": "10"})
    assert create_response.status_code == 302

    with mvp_app.app_context():
        school_class = SchoolClass.query.filter_by(code="C10A1").one()
        db.session.add(Student(code="S1001", full_name="Nguyễn Văn A", class_id=school_class.id))
        db.session.commit()
        class_id = school_class.id

    blocked_delete = client.post(f"/classes/{class_id}/delete", follow_redirects=True)
    assert "Không thể xóa lớp còn học sinh." in blocked_delete.get_data(as_text=True)


def test_student_crud_search_filter_pagination(mvp_app) -> None:
    client = mvp_app.test_client()
    login_admin(client)

    with mvp_app.app_context():
        school_class = SchoolClass(code="C11A1", name="Lớp 11A1", grade_level="11")
        db.session.add(school_class)
        db.session.commit()
        class_id = school_class.id

    response = client.post(
        "/students/new",
        data={
            "code": "S2001",
            "full_name": "Trần Bình",
            "gender": "1",
            "class_id": str(class_id),
            "average_score": "8.5",
            "learning_status": "Đang học",
        },
    )
    assert response.status_code == 302

    list_response = client.get(f"/students/?q=S2001&class_id={class_id}&page=1")
    assert list_response.status_code == 200
    assert "Trần Bình" in list_response.get_data(as_text=True)

    invalid = client.post(
        "/students/new",
        data={"code": "S2002", "full_name": "Sai điểm", "average_score": "11"},
        follow_redirects=True,
    )
    assert "Điểm trung bình phải từ 0 đến 10." in invalid.get_data(as_text=True)


def test_teacher_validation_and_crud(mvp_app) -> None:
    client = mvp_app.test_client()
    login_admin(client)

    invalid_email = client.post(
        "/teachers/new",
        data={"code": "GV100", "full_name": "Giáo viên A", "email": "bad-email", "phone": "0912345678"},
        follow_redirects=True,
    )
    assert "Email không hợp lệ." in invalid_email.get_data(as_text=True)

    invalid_phone = client.post(
        "/teachers/new",
        data={"code": "GV101", "full_name": "Giáo viên B", "email": "b@example.local", "phone": "abc"},
        follow_redirects=True,
    )
    assert "Số điện thoại không hợp lệ." in invalid_phone.get_data(as_text=True)

    created = client.post(
        "/teachers/new",
        data={
            "code": "GV102",
            "full_name": "Giáo viên C",
            "email": "c@example.local",
            "phone": "0912345678",
            "subject": "Toán",
            "status": "active",
        },
    )
    assert created.status_code == 302
    assert client.get("/teachers/?status=active").status_code == 200


def test_account_creation_requires_admin_and_hashes_password(mvp_app) -> None:
    client = mvp_app.test_client()
    login_admin(client)

    response = client.post(
        "/auth/accounts",
        data={
            "username": "teacher2",
            "full_name": "Teacher Two",
            "email": "teacher2@example.local",
            "password": "Teacher123",
            "role": "teacher",
            "status": "active",
        },
    )
    assert response.status_code == 302

    with mvp_app.app_context():
        user = User.query.filter_by(username="teacher2").one()
        assert user.role == Role.TEACHER.value
        assert user.password_hash != "Teacher123"
        user_id = user.id

    status_response = client.post(f"/auth/accounts/{user_id}/status", data={"status": "locked"})
    assert status_response.status_code == 302

    with mvp_app.app_context():
        user = db.session.get(User, user_id)
        assert user.status == "locked"
