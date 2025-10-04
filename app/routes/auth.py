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
def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    csrf_token: str = Form(...),
    db: Session = Depends(get_db),
):
    """Process login"""
    # Debug CSRF
    csrf_session = request.session.get("csrf_token")
    print(f"DBG csrf_session={csrf_session}, csrf_form={csrf_token}")
    
    # CSRF validation
    if request.session.get("csrf_token") != csrf_token:
        print(f"CSRF validation failed: session={csrf_session}, form={csrf_token}")
        raise HTTPException(status_code=400, detail="Invalid CSRF")

    # Find user
    user = db.query(User).filter(User.username == username).first()
    if not user:
        print(f"User not found: {username}")
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Verify password with bcrypt puro (hash está em bytes)
    try:
        import bcrypt
        ok = bcrypt.checkpw(password.encode("utf-8"), user.password_hash)
        print(f"Password verify result: {ok}")
    except Exception as e:
        print(f"DBG verify error: {e}, type: {type(user.password_hash)}")
        raise HTTPException(status_code=500, detail="Password verify error")

    if not ok:
        print(f"Password verification failed for user: {username}")
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Create session using the correct structure
    from ..auth import create_user_session
    create_user_session(request, user)
    print(f"Session created for user: {username} (role: {user.role})")
    
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
