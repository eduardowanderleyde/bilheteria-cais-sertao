"""Sales routes"""
from fastapi import APIRouter, Request, Depends, Form, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from typing import Optional
from ..db import get_db
from ..models import Order, OrderItem, User, OrderEvent
from ..auth import require_auth, get_user_info, can_delete, set_csrf_token
from ..schemas import OrderCreate, OrderItemCreate, TicketType, PaymentMethod

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/sell", response_class=HTMLResponse)
async def sell_page(request: Request):
    """Sales page"""
    user = require_auth(request)
    csrf_token = set_csrf_token(request)
    
    return templates.TemplateResponse("sell.html", {
        "request": request,
        "user": get_user_info(request),
        "csrf_token": csrf_token
    })

@router.post("/sell")
async def create_sale(
    request: Request,
    qtd_inteira: int = Form(0),
    qtd_meia: int = Form(0),
    qtd_gratuita: int = Form(0),
    reason_meia: Optional[str] = Form(None),
    reason_gratuita: Optional[str] = Form(None),
    name: Optional[str] = Form(None),
    state: Optional[str] = Form(None),
    city: Optional[str] = Form(None),
    note: Optional[str] = Form(None),
    payment_method: str = Form(...),
    csrf_token: str = Form(...),
    db: Session = Depends(get_db)
):
    """Create a new sale"""
    user = require_auth(request)
    
    # Validate CSRF token
    from ..auth import validate_csrf_token
    if not validate_csrf_token(request, csrf_token):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid CSRF token"
        )
    
    # Validate quantities
    if qtd_inteira + qtd_meia + qtd_gratuita <= 0:
        return RedirectResponse("/sell", status_code=status.HTTP_303_SEE_OTHER)
    
    try:
        # Create order
        order = Order(
            user_id=user["id"],
            channel="balcao",
            payment_method=payment_method,
            state=state.upper() if state else None,
            city=city,
            note=note
        )
        db.add(order)
        db.flush()  # Get the ID
        
        # Create order items
        items = [
            ("inteira", qtd_inteira, 1000, None),
            ("meia", qtd_meia, 500, reason_meia),
            ("gratuita", qtd_gratuita, 0, reason_gratuita),
        ]
        
        for ticket_type, qty, price, reason in items:
            if qty > 0:
                item = OrderItem(
                    order_id=order.id,
                    ticket_type=ticket_type,
                    qty=qty,
                    unit_price_cents=price,
                    discount_reason=reason
                )
                db.add(item)
        
        # Log the event
        event = OrderEvent(
            order_id=order.id,
            action="created",
            user_id=user["id"],
            ip_address=request.client.host if request.client else None
        )
        db.add(event)
        
        db.commit()
        return RedirectResponse("/dashboard", status_code=status.HTTP_303_SEE_OTHER)
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar venda: {str(e)}"
        )

@router.post("/orders/{order_id}/delete")
async def delete_order(
    order_id: int,
    request: Request,
    reason: str = Form(""),
    db: Session = Depends(get_db)
):
    """Soft delete an order"""
    user = require_auth(request)
    
    # Check permissions
    if not can_delete(user["role"]):
        return RedirectResponse("/unauthorized", status_code=status.HTTP_303_SEE_OTHER)
    
    # Get order
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.deleted_at.is_(None)
    ).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pedido não encontrado"
        )
    
    # Check if it's from today (optional security measure)
    today = datetime.now().date()
    if order.created_at.date() != today:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Só é possível excluir pedidos do dia atual"
        )
    
    try:
        # Soft delete
        order.deleted_at = datetime.now()
        
        # Log the event
        event = OrderEvent(
            order_id=order.id,
            action="deleted",
            user_id=user["id"],
            reason=reason,
            ip_address=request.client.host if request.client else None
        )
        db.add(event)
        
        db.commit()
        return RedirectResponse("/dashboard", status_code=status.HTTP_303_SEE_OTHER)
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao excluir pedido: {str(e)}"
        )
