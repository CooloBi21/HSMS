from __future__ import annotations

from pathlib import Path


def test_docker_compose_declares_required_services_and_networks() -> None:
    compose = Path("docker-compose.yml").read_text(encoding="utf-8")

    for service in ("hsms-web:", "postgres:", "nginx:", "cloudflared:", "backup:"):
        assert service in compose

    assert "hsms-private:" in compose
    assert "postgres_data:" in compose
    assert "restart: unless-stopped" in compose


def test_docker_compose_uses_service_names_not_container_localhost() -> None:
    compose = Path("docker-compose.yml").read_text(encoding="utf-8")

    assert "@postgres:5432/" in compose
    assert "127.0.0.1:8080:80" in compose
    assert "localhost:5432" not in compose
    assert "localhost:80" not in compose
    assert '"5432:5432"' not in compose
    assert "'5432:5432'" not in compose


def test_nginx_proxies_to_hsms_web_with_forwarded_headers() -> None:
    nginx = Path("nginx/hsms.conf").read_text(encoding="utf-8")

    assert "server hsms-web:8000;" in nginx
    assert "proxy_pass http://hsms_web" in nginx
    assert "proxy_set_header X-Forwarded-For" in nginx
    assert "proxy_set_header X-Forwarded-Proto" in nginx
    assert "client_max_body_size 10m;" in nginx
    assert "server_tokens off;" in nginx


def test_docker_image_and_backup_do_not_embed_secrets() -> None:
    dockerfile = Path("Dockerfile").read_text(encoding="utf-8")
    backup = Path("docker/backup-postgres.sh").read_text(encoding="utf-8")
    dockerignore = Path(".dockerignore").read_text(encoding="utf-8")

    assert "USER hsms" in dockerfile
    assert "gunicorn" in dockerfile
    assert "POSTGRES_PASSWORD=hsms" not in dockerfile
    assert "pg_dump" in backup
    assert ".env" in dockerignore
    assert "backups" in dockerignore
    assert "data" in dockerignore
