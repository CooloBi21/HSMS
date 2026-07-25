from __future__ import annotations

from decimal import Decimal

import pytest

from app import create_app
from app.extensions import db
from app.models.academic import SchoolClass, Student
from app.models.auth import ActivityLog, Role
from app.models.operations import AdmissionApplication
from app.services.admission_web_service import AdmissionWebService
from app.services.auth_service import AuthService
from app.services.mvp_service import ValidationError


@pytest.fixture()
def admission_app():
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        admin = AuthService.create_user("admin", "Admin", "Admin123", Role.ADMIN)
        school_class = SchoolClass(code="C10A1", name="Lớp 10A1", grade_level="10")
        db.session.add(school_class)
        db.session.commit()
        yield app, admin, school_class
        db.session.remove()
        db.drop_all()


def login_admin(client):
    return client.post("/auth/login", data={"username": "admin", "password": "Admin123"})


def test_receive_screen_and_enroll_application_service(admission_app) -> None:
    app, admin, school_class = admission_app
    with app.app_context():
        application = AdmissionWebService.receive_application(
            {
                "full_name": "Nguyễn Thí Sinh",
                "gender": "1",
                "admission_score": "7.25",
                "desired_class_id": str(school_class.id),
                "parent_name": "Nguyễn Phụ Huynh",
                "parent_phone": "0900000000",
            },
            admin,
        )

        assert application.application_code.startswith("TS")
        assert application.status == "pending"

        AdmissionWebService.auto_screen(application.id, admin, Decimal("6.0"))
        assert application.status == "approved"

        student_code = AdmissionWebService.enroll(application.id, admin)
        student = Student.query.filter_by(code=student_code).one()

        assert student.full_name == "Nguyễn Thí Sinh"
        assert student.class_id == school_class.id
        assert application.status == "enrolled"
        assert application.student_id == student.id
        assert ActivityLog.query.filter_by(module="admissions").count() >= 3


def test_reject_application_below_threshold(admission_app) -> None:
    app, admin, school_class = admission_app
    with app.app_context():
        application = AdmissionWebService.receive_application(
            {
                "full_name": "Trần Không Đạt",
                "admission_score": "4.5",
                "desired_class_id": str(school_class.id),
            },
            admin,
        )

        AdmissionWebService.auto_screen(application.id, admin, Decimal("5.0"))

        assert application.status == "rejected"
        with pytest.raises(ValidationError):
            AdmissionWebService.enroll(application.id, admin)


def test_admission_backend_validation(admission_app) -> None:
    app, admin, *_ = admission_app
    with app.app_context():
        with pytest.raises(ValidationError):
            AdmissionWebService.receive_application({"full_name": "", "admission_score": "7"}, admin)

        with pytest.raises(ValidationError):
            AdmissionWebService.receive_application({"full_name": "Sai Điểm", "admission_score": "12"}, admin)


def test_admission_routes_integration(admission_app) -> None:
    app, _, school_class = admission_app
    client = app.test_client()
    login_admin(client)

    create_response = client.post(
        "/admissions/new",
        data={
            "full_name": "Lê Route",
            "gender": "0",
            "admission_score": "8",
            "desired_class_id": str(school_class.id),
            "status": "pending",
        },
    )
    assert create_response.status_code == 302

    with app.app_context():
        application = AdmissionApplication.query.filter_by(full_name="Lê Route").one()
        application_id = application.id

    list_response = client.get("/admissions/?q=Route&status=pending")
    assert list_response.status_code == 200
    assert "Lê Route" in list_response.get_data(as_text=True)

    screen_response = client.post(f"/admissions/{application_id}/screen")
    assert screen_response.status_code == 302

    enroll_response = client.post(f"/admissions/{application_id}/enroll", follow_redirects=True)
    assert "Đã nhập học và cấp mã học sinh" in enroll_response.get_data(as_text=True)

    delete_response = client.post(f"/admissions/{application_id}/delete", follow_redirects=True)
    assert "Không thể xóa hồ sơ đã nhập học." in delete_response.get_data(as_text=True)


def test_admission_requires_permission(admission_app) -> None:
    app, *_ = admission_app
    with app.app_context():
        AuthService.create_user("student", "Student", "Student123", Role.STUDENT)

    client = app.test_client()
    client.post("/auth/login", data={"username": "student", "password": "Student123"})

    assert client.get("/admissions/").status_code == 403
