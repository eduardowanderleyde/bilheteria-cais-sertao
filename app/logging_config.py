"""
Logging configuration for the application
"""
import logging
import sys
from typing import Dict, Any
from datetime import datetime
import json
from app.config import get_settings


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON"""
        log_entry: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields
        if hasattr(record, "user_id"):
            log_entry["user_id"] = record.user_id
        if hasattr(record, "request_id"):
            log_entry["request_id"] = record.request_id
        if hasattr(record, "ip_address"):
            log_entry["ip_address"] = record.ip_address
        
        return json.dumps(log_entry, ensure_ascii=False)


def setup_logging() -> None:
    """Setup application logging"""
    settings = get_settings()
    
    # Create logger
    logger = logging.getLogger("bilheteria")
    logger.setLevel(getattr(logging, settings.log_level.upper()))
    
    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, settings.log_level.upper()))
    
    # Use JSON formatter in production, simple formatter in development
    if settings.debug:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
    else:
        formatter = JSONFormatter()
    
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Prevent duplicate logs
    logger.propagate = False


def get_logger(name: str) -> logging.Logger:
    """Get logger instance"""
    return logging.getLogger(f"bilheteria.{name}")


def log_user_action(
    logger: logging.Logger,
    action: str,
    user_id: str = None,
    details: Dict[str, Any] = None
) -> None:
    """Log user action with structured data"""
    extra = {"action": action}
    if user_id:
        extra["user_id"] = user_id
    if details:
        extra.update(details)
    
    logger.info(f"User action: {action}", extra=extra)


def log_security_event(
    logger: logging.Logger,
    event: str,
    ip_address: str = None,
    user_id: str = None,
    details: Dict[str, Any] = None
) -> None:
    """Log security event"""
    extra = {"security_event": event}
    if ip_address:
        extra["ip_address"] = ip_address
    if user_id:
        extra["user_id"] = user_id
    if details:
        extra.update(details)
    
    logger.warning(f"Security event: {event}", extra=extra)
