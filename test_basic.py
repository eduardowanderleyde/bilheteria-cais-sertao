"""Basic tests for the bilheteria system"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db import get_db, Base
from app.models import User
from app.auth import hash_password

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="module")
def client():
    """Test client"""
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="module")
def test_user():
    """Create test user"""
    db = TestingSessionLocal()
    user = User(
        username="testuser",
        password_hash=hash_password("testpass"),
        role="bilheteira",
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    yield user
    db.close()

def test_health_check(client):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_root_redirect(client):
    """Test root redirect"""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307  # Redirect

def test_login_page(client):
    """Test login page"""
    response = client.get("/auth/login")
    assert response.status_code == 200
    assert "login" in response.text.lower()

def test_login_success(client, test_user):
    """Test successful login"""
    response = client.post("/auth/login", data={
        "username": "testuser",
        "password": "testpass",
        "csrf_token": "test_token"  # In real tests, get this from the login page
    })
    # Should redirect to dashboard
    assert response.status_code in [200, 303, 307]

def test_login_failure(client):
    """Test failed login"""
    response = client.post("/auth/login", data={
        "username": "wronguser",
        "password": "wrongpass",
        "csrf_token": "test_token"
    })
    assert response.status_code == 400

def test_dashboard_requires_auth(client):
    """Test dashboard requires authentication"""
    response = client.get("/dashboard", follow_redirects=False)
    assert response.status_code in [401, 403, 307]  # Should redirect or deny

def test_unauthorized_page(client):
    """Test unauthorized page"""
    response = client.get("/auth/unauthorized")
    assert response.status_code == 200
    assert "unauthorized" in response.text.lower()

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
