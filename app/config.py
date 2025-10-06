"""
Configuration management for the application
"""
import os
from typing import Optional
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Database
    database_url: str = Field(
        default="sqlite:///./bilheteria.db",
        env="DATABASE_URL",
        description="Database connection URL"
    )
    
    # Security
    secret_key: str = Field(
        default="change-me-in-production",
        env="SECRET_KEY",
        description="Secret key for session management"
    )
    secure_cookies: bool = Field(
        default=False,
        env="SECURE_COOKIES",
        description="Enable secure cookies (HTTPS only)"
    )
    
    # Application
    debug: bool = Field(
        default=True,
        env="DEBUG",
        description="Enable debug mode"
    )
    host: str = Field(
        default="127.0.0.1",
        env="HOST",
        description="Host to bind the application"
    )
    port: int = Field(
        default=8000,
        env="PORT",
        description="Port to bind the application"
    )
    
    # Admin credentials
    admin_username: str = Field(
        default="admin",
        env="ADMIN_USERNAME",
        description="Admin username"
    )
    admin_password: str = Field(
        default="change-me",
        env="ADMIN_PASSWORD",
        description="Admin password"
    )
    
    # Other users
    gestora_password: str = Field(
        default="gestora123",
        env="GESTORA_PASSWORD",
        description="Gestora password"
    )
    bilheteira_password: str = Field(
        default="bilheteira123",
        env="BILHETEIRA_PASSWORD",
        description="Bilheteira password"
    )
    
    # Test credentials
    test_username: str = Field(
        default="admin",
        env="TEST_USERNAME",
        description="Test username"
    )
    test_password: str = Field(
        default="test123",
        env="TEST_PASSWORD",
        description="Test password"
    )
    
    # Logging
    log_level: str = Field(
        default="INFO",
        env="LOG_LEVEL",
        description="Logging level"
    )
    
    # Performance
    max_upload_size: int = Field(
        default=10 * 1024 * 1024,  # 10MB
        env="MAX_UPLOAD_SIZE",
        description="Maximum upload size in bytes"
    )
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings"""
    return settings


def is_production() -> bool:
    """Check if running in production mode"""
    return not settings.debug and settings.secure_cookies


def get_database_url() -> str:
    """Get database URL with proper configuration"""
    url = settings.database_url
    
    # Add connection parameters for SQLite
    if url.startswith("sqlite"):
        if "?" not in url:
            url += "?check_same_thread=False"
    
    return url
