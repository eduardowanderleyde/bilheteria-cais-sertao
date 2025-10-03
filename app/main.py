"""Main FastAPI application"""
import os
from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import RedirectResponse
from .db import engine, Base, get_db
from .models import User, Order, OrderItem, Group, OrderEvent, Sale
from .auth import get_user_info, require_auth
from .routes import auth, dashboard, sales, groups, reports, admin

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="Bilheteria Cais do Sertão",
    description="Sistema de bilheteria para o Museu Cais do Sertão",
    version="1.0.0"
)

# Security middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # Configure for production
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Session middleware
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SECRET_KEY", "change-me"),
    https_only=os.getenv("SECURE_COOKIES", "false").lower() == "true",
    same_site="lax",
    session_cookie="session",
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["authentication"])
app.include_router(dashboard.router, tags=["dashboard"])
app.include_router(sales.router, tags=["sales"])
app.include_router(groups.router, tags=["groups"])
app.include_router(reports.router, prefix="/reports", tags=["reports"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])

# Root redirect
@app.get("/")
async def root(request: Request):
    """Root endpoint - redirect to dashboard or login"""
    user = get_user_info(request)
    if user.get("username"):
        return RedirectResponse("/dashboard")
    return RedirectResponse("/auth/login")

# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "1.0.0"}

# Template context processor
@app.middleware("http")
async def add_template_context(request: Request, call_next):
    """Add common context to all templates"""
    response = await call_next(request)
    return response

# Template helper functions
def get_template_context(request: Request, **kwargs):
    """Get template context with user info"""
    context = {
        "request": request,
        "user": get_user_info(request),
        **kwargs
    }
    return context
