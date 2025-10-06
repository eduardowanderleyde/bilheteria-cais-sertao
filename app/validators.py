"""
Data validation utilities
"""
import re
from typing import Any, Dict, List, Optional
from datetime import datetime, date
from pydantic import BaseModel, field_validator, Field
from enum import Enum
from app.config import get_settings


class TicketType(str, Enum):
    """Ticket types"""
    INTEIRA = "inteira"
    MEIA = "meia"
    GRATUITA = "gratuita"


class PaymentMethod(str, Enum):
    """Payment methods"""
    CREDITO = "credito"
    DEBITO = "debito"
    PIX = "pix"
    DINHEIRO = "dinheiro"


class DiscountReason(str, Enum):
    """Discount reasons for half/free tickets"""
    # Half ticket reasons
    ESTUDANTE_PUBLICA = "estudante_publica"
    ESTUDANTE_PRIVADA = "estudante_privada"
    IDOSO = "idoso"
    PCD = "pcd"
    PROFESSOR = "professor"
    
    # Free ticket reasons
    CRIANCA = "crianca"
    FUNCIONARIO = "funcionario"
    VISITA_TECNICA = "visita_tecnica"
    EVENTO_ESPECIAL = "evento_especial"


class SaleCreate(BaseModel):
    """Sale creation validation"""
    ticket_type: TicketType
    quantity: int = Field(..., ge=1, le=100)
    payment_method: PaymentMethod
    discount_reason: Optional[DiscountReason] = None
    customer_name: Optional[str] = Field(None, max_length=120)
    customer_state: Optional[str] = Field(None, max_length=2)
    customer_city: Optional[str] = Field(None, max_length=120)
    notes: Optional[str] = Field(None, max_length=500)
    
    @field_validator('customer_state')
    @classmethod
    def validate_state(cls, v):
        if v and len(v) != 2:
            raise ValueError('State must be 2 characters')
        return v.upper() if v else v
    
    @field_validator('customer_name')
    @classmethod
    def validate_name(cls, v):
        if v and not re.match(r'^[a-zA-ZÀ-ÿ\s]+$', v):
            raise ValueError('Name can only contain letters and spaces')
        return v
    
    @field_validator('discount_reason')
    @classmethod
    def validate_discount_reason(cls, v, info):
        ticket_type = info.data.get('ticket_type') if info.data else None
        if ticket_type in ['meia', 'gratuita'] and not v:
            raise ValueError(f'Discount reason required for {ticket_type} tickets')
        return v


class GroupCreate(BaseModel):
    """Group creation validation"""
    institution: str = Field(..., max_length=160)
    size: int = Field(..., ge=1, le=200)
    state: str = Field(..., max_length=2)
    city: str = Field(..., max_length=120)
    scheduled: bool = True
    contact_name: Optional[str] = Field(None, max_length=120)
    contact_phone: Optional[str] = Field(None, max_length=40)
    price_total: Optional[float] = Field(None, ge=0)
    visit_date: Optional[date] = None
    
    @field_validator('state')
    @classmethod
    def validate_state(cls, v):
        if len(v) != 2:
            raise ValueError('State must be 2 characters')
        return v.upper()
    
    @field_validator('contact_phone')
    @classmethod
    def validate_phone(cls, v):
        if v and not re.match(r'^\(\d{2}\)\s\d{4,5}-\d{4}$', v):
            raise ValueError('Phone must be in format (XX) XXXX-XXXX or (XX) XXXXX-XXXX')
        return v
    
    @field_validator('visit_date')
    @classmethod
    def validate_visit_date(cls, v):
        if v and v < date.today():
            raise ValueError('Visit date cannot be in the past')
        return v


class UserCreate(BaseModel):
    """User creation validation"""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8, max_length=128)
    role: str = Field(..., pattern='^(admin|gestora|bilheteira)$')
    is_active: bool = True
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Username can only contain letters, numbers and underscores')
        return v.lower()
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one number')
        return v


class ReportFilter(BaseModel):
    """Report filter validation"""
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    state: Optional[str] = Field(None, max_length=2)
    payment_method: Optional[PaymentMethod] = None
    ticket_type: Optional[TicketType] = None
    limit: int = Field(100, ge=1, le=1000)
    offset: int = Field(0, ge=0)
    
    @field_validator('end_date')
    @classmethod
    def validate_date_range(cls, v, info):
        start_date = info.data.get('start_date') if info.data else None
        if start_date and v and v < start_date:
            raise ValueError('End date must be after start date')
        return v
    
    @field_validator('state')
    @classmethod
    def validate_state(cls, v):
        if v and len(v) != 2:
            raise ValueError('State must be 2 characters')
        return v.upper() if v else v


def validate_environment() -> Dict[str, Any]:
    """Validate environment configuration"""
    settings = get_settings()
    errors = []
    warnings = []
    
    # Check required settings
    if settings.secret_key == "change-me-in-production":
        errors.append("SECRET_KEY must be changed in production")
    
    if settings.admin_password == "change-me":
        errors.append("ADMIN_PASSWORD must be changed in production")
    
    # Check database URL
    if settings.database_url.startswith("sqlite") and not settings.debug:
        warnings.append("SQLite is not recommended for production")
    
    # Check security settings
    if not settings.secure_cookies and not settings.debug:
        warnings.append("SECURE_COOKIES should be enabled in production")
    
    return {
        "errors": errors,
        "warnings": warnings,
        "is_valid": len(errors) == 0
    }
