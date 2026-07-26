from __future__ import annotations

import pytest
from sqlalchemy import func

from app import create_app
from app.extensions import db
from app.models.academic import SchoolClass, Student, Teacher
from app.models.auth import Role
from app.models.operations import AdmissionApplication
from app.services.auth_service import AuthService
from app.services.demo_seed_service import DemoSeedService


@pytest.fixture()
def seeded_app():
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        AuthService.create_user("admin", "Admin", "Admin123", Role.ADMIN)
        DemoSeedService.seed()
        yield app
        db.session.remove()
        db.drop_all()


def login_admin(client):
    return client.post("/auth/login", data={"username": "admin", "password": "Admin123"})


def test_nav_exposes_logout_after_login(seeded_app) -> None:
    client = seeded_app.test_client()
    login_admin(client)

    response = client.get("/")
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "/auth/logout" in html
    assert "logout-button" in html


def test_demo_seed_creates_balanced_school_data(seeded_app) -> None:
    with seeded_app.app_context():
        max_class_size = (
            db.session.query(func.count(Student.id))
            .join(SchoolClass, Student.class_id == SchoolClass.id)
            .filter(SchoolClass.code.like("DEMO%"))
            .group_by(SchoolClass.id)
            .order_by(func.count(Student.id).desc())
            .first()[0]
        )

        assert Student.query.filter(Student.code.like("HSDEMO%")).count() == 500
        assert Teacher.query.filter(Teacher.code.like("GVDEMO%")).count() == 100
        assert SchoolClass.query.filter(SchoolClass.code.like("DEMO%")).count() == 22
        assert AdmissionApplication.query.filter_by(status="pending").count() >= 8
        assert max_class_size <= 45


def test_training_exams_finance_pages_render_seeded_data(seeded_app) -> None:
    client = seeded_app.test_client()
    login_admin(client)

    for path in ("/training/", "/exams/", "/finance/"):
        response = client.get(path)
        assert response.status_code == 200
        assert "metric-box" in response.get_data(as_text=True)
