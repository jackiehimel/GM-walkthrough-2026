"""Smoke tests — verify scaffold boots and auth works."""
import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture()
def client():
    with TestClient(app) as c:
        yield c


def test_root_redirects_to_login(client):
    resp = client.get("/", follow_redirects=False)
    assert resp.status_code == 302
    assert "/login" in resp.headers["location"]


def test_login_page_renders(client):
    resp = client.get("/login")
    assert resp.status_code == 200
    assert "confirmation" in resp.text.lower()


def test_staff_login_page_renders(client):
    resp = client.get("/staff/login")
    assert resp.status_code == 200
    assert "employee" in resp.text.lower()


def test_guest_login_valid(client):
    resp = client.post(
        "/login",
        data={"confirmation_code": "GM-2026-001", "last_name": "Parker"},
        follow_redirects=False,
    )
    assert resp.status_code == 303
    assert "/guest" in resp.headers["location"]


def test_guest_login_invalid(client):
    resp = client.post(
        "/login",
        data={"confirmation_code": "GM-2026-001", "last_name": "WrongName"},
    )
    assert resp.status_code == 200
    assert "error" in resp.text.lower() or "invalid" in resp.text.lower()


def test_staff_login_valid(client):
    resp = client.post(
        "/staff/login",
        data={"employee_id": "EMP-2026-002", "last_name": "Wilson"},
        follow_redirects=False,
    )
    assert resp.status_code == 303
    assert "/staff" in resp.headers["location"]


def test_guest_routes_require_auth(client):
    resp = client.get("/guest", follow_redirects=False)
    # Should redirect to login
    assert resp.status_code == 303
    assert "/login" in resp.headers["location"]


def test_staff_routes_require_auth(client):
    resp = client.get("/staff", follow_redirects=False)
    # Should redirect to staff login
    assert resp.status_code == 303
    assert "/staff/login" in resp.headers["location"]
