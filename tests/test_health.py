from __future__ import annotations

from app import create_app


def test_healthcheck() -> None:
    app = create_app("testing")
    client = app.test_client()

    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"
