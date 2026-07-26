from __future__ import annotations

from pathlib import Path

from app import create_app
from app.extensions import db
from app.models.academic import SchoolClass, Student
from app.models.auth import Role
from app.services.auth_service import AuthService


def test_layout_has_mobile_offcanvas_and_viewport() -> None:
    base = Path("app/templates/layouts/base.html").read_text(encoding="utf-8")
    nav = Path("app/templates/components/nav.html").read_text(encoding="utf-8")

    assert 'name="viewport"' in base
    assert "offcanvas" in nav
    assert 'data-bs-toggle="offcanvas"' in nav
    assert "touch-target" in nav


def test_css_has_required_responsive_guards() -> None:
    css = Path("app/static/css/app.css").read_text(encoding="utf-8")

    assert "overflow-x: hidden" in css
    assert ".table-responsive" in css
    assert "min-height: 44px" in css
    assert "max-height: calc(100vh" in css
    assert "@media (max-width: 768px)" in css
    assert "@media (max-width: 420px)" in css
    assert "clamp(" in css


def test_student_role_does_not_see_admin_data_on_mobile_routes() -> None:
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        school_class = SchoolClass(code="C10", name="Lớp 10")
        student = Student(
            code="S7001",
            full_name="Học sinh Mobile",
            school_class=school_class,
        )
        other = Student(
            code="S7002",
            full_name="Dữ liệu không thuộc quyền",
            school_class=school_class,
        )
        db.session.add_all([school_class, student, other])
        db.session.commit()
        AuthService.create_user(
            "student",
            "Học sinh Mobile",
            "Student123",
            Role.STUDENT,
            student_code=student.code,
            student_id=student.id,
        )

        client = app.test_client()
        client.post(
            "/auth/login",
            data={"username": "student", "password": "Student123"},
        )
        self_profile = client.get(
            "/profiles/me",
            headers={"User-Agent": "Mobile Safari"},
        )
        admin_list = client.get(
            "/students/",
            headers={"User-Agent": "Mobile Safari"},
        )

        assert self_profile.status_code == 200
        html = self_profile.get_data(as_text=True)
        assert "Học sinh Mobile" in html
        assert "Dữ liệu không thuộc quyền" not in html
        assert admin_list.status_code == 403

        db.session.remove()
        db.drop_all()
