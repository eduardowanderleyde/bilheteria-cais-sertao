"""SQLAlchemy models for the bilheteria system"""
from sqlalchemy import Column, Integer, String, DateTime, Numeric, Boolean, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .db import Base

class User(Base):
    """User model with roles and permissions"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="bilheteira")  # admin, gestora, bilheteira
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    orders = relationship("Order", back_populates="user")

class Order(Base):
    """Order header - individual sales and group sales"""
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    channel = Column(String(20), nullable=False, default="balcao")  # balcao, grupo, online
    payment_method = Column(String(20), nullable=False)  # credito, debito, pix
    state = Column(String(2))  # UF
    city = Column(String(100))
    note = Column(Text)
    deleted_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    group = relationship("Group", back_populates="order", uselist=False, cascade="all, delete-orphan")
    events = relationship("OrderEvent", back_populates="order", cascade="all, delete-orphan")

class OrderItem(Base):
    """Order items - ticket details"""
    __tablename__ = "order_items"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    ticket_type = Column(String(20), nullable=False)  # inteira, meia, gratuita
    qty = Column(Integer, nullable=False)
    unit_price_cents = Column(Integer, nullable=False)
    discount_reason = Column(String(50))  # motivo da meia/gratuidade
    
    # Relationships
    order = relationship("Order", back_populates="items")

class Group(Base):
    """Group visit metadata"""
    __tablename__ = "groups"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    visit_type = Column(String(20), nullable=False)  # agendada, espontanea
    has_oficio = Column(Boolean, default=False, nullable=False)
    institution_name = Column(String(200))
    total_students = Column(Integer, default=0)
    total_teachers = Column(Integer, default=0)
    responsible_name = Column(String(100))
    state = Column(String(2))
    city = Column(String(100))
    ies_municipio = Column(String(100))
    scheduled_date = Column(DateTime)
    
    # Relationships
    order = relationship("Order", back_populates="group")

class OrderEvent(Base):
    """Audit log for order actions"""
    __tablename__ = "order_events"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    action = Column(String(50), nullable=False)  # created, updated, deleted
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    reason = Column(Text)
    ip_address = Column(String(45))  # IPv6 compatible
    
    # Relationships
    order = relationship("Order", back_populates="events")
    user = relationship("User")

# Legacy table for compatibility (will be migrated)
class Sale(Base):
    """Legacy sales table for compatibility"""
    __tablename__ = "sales"
    
    id = Column(Integer, primary_key=True, index=True)
    sold_at = Column(DateTime, server_default=func.now())
    ticket_type = Column(String(20), nullable=False)
    qty = Column(Integer, nullable=False)
    unit_price_cents = Column(Integer, nullable=False)
    operator_username = Column(String(50), nullable=False)
    name = Column(String(100))
    state = Column(String(2))
    city = Column(String(100))
    note = Column(Text)
    payment_method = Column(String(20))

class GroupVisit(Base):
    """Group visits model for detailed group tracking"""
    __tablename__ = "group_visits"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, nullable=False)  # data da visita
    institution = Column(String(160))  # escola/instituição
    size = Column(Integer, nullable=False)  # nº pessoas
    state = Column(String(2))  # UF
    city = Column(String(120))  # cidade
    scheduled = Column(Boolean, default=True)  # agendada?
    contact_name = Column(String(120))
    contact_phone = Column(String(40))
    price_total = Column(Numeric(10,2), default=0)  # opcional
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships - removed for now as it's not needed for basic functionality
