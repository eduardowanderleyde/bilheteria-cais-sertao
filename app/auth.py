"""Authentication and authorization utilities"""
import os
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from .db import get_db
from .models import User
import bcrypt

# Security configuration
SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Session configuration
SESSION_KEY = "user_session"

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_current_user(request: Request) -> Optional[Dict[str, Any]]:
    """Get current user from session"""
    return request.session.get(SESSION_KEY)

def require_auth(request: Request) -> Dict[str, Any]:
    """Require authentication - raises 401 if not authenticated"""
    user = get_current_user(request)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    return user

def require_role(request: Request, allowed_roles: set) -> Dict[str, Any]:
    """Require specific role - raises 403 if not authorized"""
    user = require_auth(request)
    if user.get("role") not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    return user

def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """Authenticate user with username and password"""
    user = db.query(User).filter(
        User.username == username,
        User.is_active == True
    ).first()
    
    if not user or not verify_password(password, user.password_hash):
        return None
    
    return user

def create_user_session(request: Request, user: User) -> None:
    """Create user session"""
    request.session[SESSION_KEY] = {
        "id": user.id,
        "username": user.username,
        "role": user.role,
        "is_active": user.is_active
    }

def clear_user_session(request: Request) -> None:
    """Clear user session"""
    request.session.pop(SESSION_KEY, None)

def get_user_info(request: Request) -> Dict[str, Any]:
    """Get complete user information for templates"""
    user_data = request.session.get(SESSION_KEY)
    if isinstance(user_data, dict):
        return {
            "id": user_data.get("id"),
            "username": user_data.get("username"),
            "role": user_data.get("role"),
            "is_active": user_data.get("is_active")
        }
    return {"username": user_data}

# Role-based access control
def can_delete(user_role: str) -> bool:
    """Check if user can delete records"""
    return user_role in ["admin", "gestora"]

def can_edit(user_role: str) -> bool:
    """Check if user can edit records"""
    return user_role in ["admin", "gestora"]

def can_view_admin(user_role: str) -> bool:
    """Check if user can view admin panel"""
    return user_role in ["admin", "gestora"]

def can_export(user_role: str) -> bool:
    """Check if user can export reports"""
    return True  # All roles can export

# CSRF protection
def generate_csrf_token() -> str:
    """Generate CSRF token"""
    return secrets.token_urlsafe(32)

def validate_csrf_token(request: Request, token: str) -> bool:
    """Validate CSRF token"""
    session_token = request.session.get("csrf_token")
    return session_token and secrets.compare_digest(session_token, token)

def set_csrf_token(request: Request) -> str:
    """Set CSRF token in session and return it"""
    token = generate_csrf_token()
    request.session["csrf_token"] = token
    return token
