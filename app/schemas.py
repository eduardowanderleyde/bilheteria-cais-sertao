"""Pydantic schemas for request/response validation"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    GESTORA = "gestora"
    BILHETEIRA = "bilheteira"

class TicketType(str, Enum):
    INTEIRA = "inteira"
    MEIA = "meia"
    GRATUITA = "gratuita"

class PaymentMethod(str, Enum):
    CREDITO = "credito"
    DEBITO = "debito"
    PIX = "pix"

class Channel(str, Enum):
    BALCAO = "balcao"
    GRUPO = "grupo"
    ONLINE = "online"

class VisitType(str, Enum):
    AGENDADA = "agendada"
    ESPONTANEA = "espontanea"

# User schemas
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    role: UserRole = UserRole.BILHETEIRA

class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=100)

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Login schemas
class LoginRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=100)

class LoginResponse(BaseModel):
    user: UserResponse
    message: str = "Login realizado com sucesso"

# Order item schemas
class OrderItemCreate(BaseModel):
    ticket_type: TicketType
    qty: int = Field(..., ge=0, le=100)
    discount_reason: Optional[str] = Field(None, max_length=50)

class OrderItemResponse(OrderItemCreate):
    id: int
    unit_price_cents: int
    
    class Config:
        from_attributes = True

# Order schemas
class OrderCreate(BaseModel):
    channel: Channel = Channel.BALCAO
    payment_method: PaymentMethod
    state: Optional[str] = Field(None, max_length=2)
    city: Optional[str] = Field(None, max_length=100)
    note: Optional[str] = Field(None, max_length=500)
    items: List[OrderItemCreate] = Field(..., min_items=1)
    
    @validator('state')
    def validate_state(cls, v):
        if v and len(v) != 2:
            raise ValueError('State must be 2 characters (UF)')
        return v.upper() if v else v

class OrderResponse(BaseModel):
    id: int
    created_at: datetime
    channel: str
    payment_method: str
    state: Optional[str]
    city: Optional[str]
    note: Optional[str]
    items: List[OrderItemResponse]
    user: UserResponse
    
    class Config:
        from_attributes = True

# Group schemas
class GroupCreate(BaseModel):
    visit_type: VisitType
    has_oficio: bool = False
    institution_name: str = Field(..., min_length=1, max_length=200)
    responsible_name: str = Field(..., min_length=1, max_length=100)
    state: Optional[str] = Field(None, max_length=2)
    city: Optional[str] = Field(None, max_length=100)
    ies_municipio: Optional[str] = Field(None, max_length=100)
    scheduled_date: Optional[datetime] = None
    total_students: int = Field(0, ge=0, le=1000)
    total_teachers: int = Field(0, ge=0, le=100)
    note: Optional[str] = Field(None, max_length=500)
    payment_method: PaymentMethod
    items: List[OrderItemCreate] = Field(..., min_items=1)
    
    @validator('state')
    def validate_state(cls, v):
        if v and len(v) != 2:
            raise ValueError('State must be 2 characters (UF)')
        return v.upper() if v else v

class GroupResponse(BaseModel):
    id: int
    visit_type: str
    has_oficio: bool
    institution_name: str
    responsible_name: str
    state: Optional[str]
    city: Optional[str]
    ies_municipio: Optional[str]
    scheduled_date: Optional[datetime]
    total_students: int
    total_teachers: int
    order: OrderResponse
    
    class Config:
        from_attributes = True

# Report schemas
class ReportByState(BaseModel):
    state: str
    total_people: int
    total_revenue: float

class ReportByDiscountReason(BaseModel):
    reason: str
    count: int
    total_revenue: float

class ReportByPaymentMethod(BaseModel):
    payment_method: str
    count: int
    total_revenue: float

class DailyReport(BaseModel):
    date: str
    total_people: int
    total_revenue: float
    by_ticket_type: dict
    by_payment_method: dict

# Audit schemas
class AuditLogResponse(BaseModel):
    id: int
    action: str
    user: UserResponse
    created_at: datetime
    reason: Optional[str]
    ip_address: Optional[str]
    
    class Config:
        from_attributes = True
