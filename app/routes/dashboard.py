"""Dashboard routes"""
from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, date
from ..db import get_db
from ..models import Order, OrderItem, User
from ..auth import require_auth, get_user_info

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    """Main dashboard"""
    user = require_auth(request)
    
    # Get today's date
    today = date.today()
    
    # Total tickets today
    tickets_today = db.query(func.sum(OrderItem.qty)).join(Order).filter(
        func.date(Order.created_at) == today,
        Order.deleted_at.is_(None)
    ).scalar() or 0
    
    # Revenue today
    revenue_today = db.query(func.sum(OrderItem.qty * OrderItem.unit_price_cents)).join(Order).filter(
        func.date(Order.created_at) == today,
        Order.deleted_at.is_(None)
    ).scalar() or 0
    revenue_today = revenue_today / 100
    
    # Tickets by type today
    tickets_by_type = db.query(
        OrderItem.ticket_type,
        func.sum(OrderItem.qty).label('total')
    ).join(Order).filter(
        func.date(Order.created_at) == today,
        Order.deleted_at.is_(None)
    ).group_by(OrderItem.ticket_type).all()
    
    # Revenue by payment method today
    revenue_by_payment = db.query(
        Order.payment_method,
        func.sum(OrderItem.qty * OrderItem.unit_price_cents).label('total')
    ).join(OrderItem).filter(
        func.date(Order.created_at) == today,
        Order.deleted_at.is_(None)
    ).group_by(Order.payment_method).all()
    
    # Recent orders
    recent_orders = db.query(Order).filter(
        func.date(Order.created_at) == today,
        Order.deleted_at.is_(None)
    ).order_by(Order.created_at.desc()).limit(10).all()
    
    # Process data for template
    tickets_data = {item.ticket_type: item.total for item in tickets_by_type}
    payment_data = {item.payment_method: item.total / 100 for item in revenue_by_payment}
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user": get_user_info(request),
        "tickets_today": tickets_today,
        "revenue_today": f"{revenue_today:.2f}",
        "inteiras_today": tickets_data.get("inteira", 0),
        "meias_today": tickets_data.get("meia", 0),
        "gratuitas_today": tickets_data.get("gratuita", 0),
        "credito_today": f"{payment_data.get('credito', 0):.2f}",
        "debito_today": f"{payment_data.get('debito', 0):.2f}",
        "pix_today": f"{payment_data.get('pix', 0):.2f}",
        "recent_orders": recent_orders
    })
