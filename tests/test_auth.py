"""
Authentication tests
"""
import pytest
from fastapi.testclient import TestClient
from app.models import User


def test_login_page(client: TestClient):
    """Test login page loads correctly"""
    response = client.get("/auth/login")
    assert response.status_code == 200
    assert "csrf_token" in response.text


def test_login_success(client: TestClient, admin_user):
    """Test successful login"""
    response = client.post("/auth/login", data={
        "username": "admin",
        "password": "admin123",
        "csrf_token": "test-token"
    })
    # Should redirect on success
    assert response.status_code in [302, 303]


def test_login_invalid_credentials(client: TestClient):
    """Test login with invalid credentials"""
    response = client.post("/auth/login", data={
        "username": "invalid",
        "password": "invalid",
        "csrf_token": "test-token"
    })
    assert response.status_code == 401


def test_logout(client: TestClient, auth_headers):
    """Test logout functionality"""
    response = client.post("/auth/logout", headers=auth_headers)
    assert response.status_code in [302, 303]


def test_protected_route_without_auth(client: TestClient):
    """Test accessing protected route without authentication"""
    response = client.get("/dashboard")
    assert response.status_code == 401


def test_protected_route_with_auth(client: TestClient, auth_headers):
    """Test accessing protected route with authentication"""
    response = client.get("/dashboard", headers=auth_headers)
    assert response.status_code == 200
