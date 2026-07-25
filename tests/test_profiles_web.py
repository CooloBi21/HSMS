from __future__ import annotations

import pytest

from app import create_app
from app.extensions import db
from app.models.academic import SchoolClass, Student
from app.models.auth import ActivityLog, Role
from app.services.auth_service import AuthService
from app.services.mvp_service import ValidationError
from app.services.profile_service import StudentProfileService


@pytest.fixture()
def profile_app():
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        admin = AuthService.create_user("admin", "Admin", "Admin123", Role.ADMIN)
        school_class = SchoolClass(code="C10A1", name="Lớp 10A1", grade_level="10")
        student = Student(code="S5001", full_name="Nguyễn Hồ Sơ", school_class=school_class)
        db.session.add_all([school_class, student])
        db.session.commit()
        student_user = AuthService.create_user(
            "student",
            "Nguyễn Hồ Sơ",
            "Student123",
            Role.STUDENT,
            student_code=student.code,
            student_id=student.id,
        )
        yield app, admin, school_class, student, student_user
        db.session.remove()
        db.drop_all()


def login(client, username: str, password: str):
    return client.post("/auth/login", data={"username": username, "password": password})


def test_update_student_profile_service(profile_app) -> None:
    app, admin, school_class, student, _ = profile_app
    with app.app_context():
        updated = StudentProfileService.update_profile(
            student.id,
            {
                "full_name": "Nguyễn Hồ Sơ Mới",
                "gender": "1",
                "class_id": str(school_class.id),
                "learning_status": "Bảo lưu",
                "policy_type": "Hộ nghèo",
                "parent_name": "Nguyễn Phụ Huynh",
                "parent_phone": "0900000000",
                "household": "Hà Nội",
                "address": "Quận 1",
            },
            admin,
        )

        assert updated.full_name == "Nguyễn Hồ Sơ Mới"
        assert updated.learning_status == "Bảo lưu"
        assert updated.policy_type == "Hộ nghèo"
        assert updated.parent_phone == "0900000000"
        assert ActivityLog.query.filter_by(module="profiles").count() >= 1


def test_profile_backend_validation(profile_app) -> None:
    app, admin, _, student, _ = profile_app
    with app.app_context():
        with pytest.raises(ValidationError, match="Trạng thái học tập"):
            StudentProfileService.update_profile(
                student.id,
                {"full_name": "A", "learning_status": "Sai trạng thái", "parent_phone": "0900000000"},
                admin,
            )

        with pytest.raises(ValidationError, match="Số điện thoại"):
            StudentProfileService.update_profile(
                student.id,
                {"full_name": "A", "learning_status": "Đang học", "parent_phone": "abc"},
                admin,
            )


def test_profile_admin_routes(profile_app) -> None:
    app, _, school_class, student, _ = profile_app
    client = app.test_client()
    login(client, "admin", "Admin123")

    list_response = client.get("/profiles/?q=S5001")
    assert list_response.status_code == 200
    assert "Nguyễn Hồ Sơ" in list_response.get_data(as_text=True)

    edit_response = client.post(
        f"/profiles/{student.id}/edit",
        data={
            "full_name": "Nguyễn Route",
            "gender": "0",
            "class_id": str(school_class.id),
            "learning_status": "Đang học",
            "policy_type": "Vùng sâu vùng xa",
            "parent_name": "Phụ huynh",
            "parent_phone": "0911111111",
            "household": "Đà Nẵng",
            "address": "Hải Châu",
        },
    )
    assert edit_response.status_code == 302

    filtered = client.get("/profiles/?policy_type=Vùng sâu vùng xa")
    assert "Nguyễn Route" in filtered.get_data(as_text=True)


def test_student_can_only_view_self_profile(profile_app) -> None:
    app, *_ = profile_app
    client = app.test_client()
    login(client, "student", "Student123")

    self_response = client.get("/profiles/me")
    admin_profiles = client.get("/profiles/")

    assert self_response.status_code == 200
    assert "Hồ sơ của tôi" in self_response.get_data(as_text=True)
    assert admin_profiles.status_code == 403
