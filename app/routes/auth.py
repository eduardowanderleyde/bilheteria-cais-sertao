"""Authentication routes"""
from fastapi import APIRouter, Request, Form, Depends, HTTPException, status
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from ..db import get_db
from ..models import User
from ..auth import authenticate_user, create_user_session, clear_user_session, get_user_info, set_csrf_token
from ..schemas import LoginRequest, UserResponse

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Login page"""
    csrf_token = set_csrf_token(request)
    return templates.TemplateResponse("login.html", {
        "request": request,
        "no_sidebar": True,
        "csrf_token": csrf_token
    })

@router.post("/login")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    csrf_token: str = Form(...),
    db: Session = Depends(get_db)
):
    """Process login"""
    # Validate CSRF token
    from ..auth import validate_csrf_token
    if not validate_csrf_token(request, csrf_token):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid CSRF token"
        )
    
    # Authenticate user
    user = authenticate_user(db, username, password)
    if not user:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "no_sidebar": True,
            "error": "Usuário ou senha inválidos",
            "csrf_token": set_csrf_token(request)
        }, status_code=400)
    
    # Create session
    create_user_session(request, user)
    
    # Redirect to dashboard
    return RedirectResponse("/dashboard", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/logout")
async def logout(request: Request):
    """Logout user"""
    clear_user_session(request)
    return RedirectResponse("/auth/login", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/unauthorized", response_class=HTMLResponse)
async def unauthorized(request: Request):
    """Unauthorized access page"""
    return templates.TemplateResponse("unauthorized.html", {
        "request": request,
        "no_sidebar": True,
        "user": get_user_info(request)
    })
