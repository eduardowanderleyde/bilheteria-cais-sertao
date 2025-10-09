"""
Health check endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.config import get_settings
import psutil
import os

router = APIRouter(prefix="/health")


@router.get("/")
async def health_check():
    """Basic health check"""
    return {
        "status": "healthy",
        "service": "bilheteria-cais",
        "version": "1.0.0"
    }


@router.get("/ready")
async def readiness_check(db: Session = Depends(get_db)):
    """Readiness check - verifies database connectivity"""
    try:
        # Test database connection
        db.execute("SELECT 1")
        return {
            "status": "ready",
            "database": "connected"
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database not ready: {str(e)}")


@router.get("/live")
async def liveness_check():
    """Liveness check - verifies application is running"""
    settings = get_settings()
    
    # Get system metrics
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    return {
        "status": "alive",
        "memory": {
            "total": memory.total,
            "available": memory.available,
            "percent": memory.percent
        },
        "disk": {
            "total": disk.total,
            "free": disk.free,
            "percent": (disk.used / disk.total) * 100
        },
        "config": {
            "debug": settings.debug,
            "host": settings.host,
            "port": settings.port
        }
    }


@router.get("/metrics")
async def metrics():
    """Application metrics for monitoring"""
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    return {
        "memory_usage_percent": memory.percent,
        "disk_usage_percent": (disk.used / disk.total) * 100,
        "cpu_count": psutil.cpu_count(),
        "load_average": os.getloadavg() if hasattr(os, 'getloadavg') else None
    }
