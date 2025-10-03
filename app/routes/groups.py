"""Group sales routes"""
from fastapi import APIRouter, Request, Depends, Form, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from typing import Optional
from ..db import get_db
from ..models import Order, OrderItem, Group, OrderEvent
from ..auth import require_auth, get_user_info, set_csrf_token

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/groups", response_class=HTMLResponse)
async def groups_page(request: Request):
    """Groups page"""
    user = require_auth(request)
    csrf_token = set_csrf_token(request)
    
    return templates.TemplateResponse("groups.html", {
        "request": request,
        "user": get_user_info(request),
        "csrf_token": csrf_token
    })

@router.post("/groups/new")
async def create_group(
    request: Request,
    visit_type: str = Form(...),
    has_oficio: bool = Form(False),
    institution_name: str = Form(...),
    responsible_name: str = Form(...),
    state: Optional[str] = Form(None),
    city: Optional[str] = Form(None),
    ies_municipio: Optional[str] = Form(None),
    scheduled_date: Optional[str] = Form(None),
    total_students: int = Form(0),
    total_teachers: int = Form(0),
    qtd_inteira: int = Form(0),
    qtd_meia: int = Form(0),
    qtd_gratuita: int = Form(0),
    reason_meia: Optional[str] = Form(None),
    reason_gratuita: Optional[str] = Form(None),
    note: Optional[str] = Form(None),
    payment_method: str = Form(...),
    csrf_token: str = Form(...),
    db: Session = Depends(get_db)
):
    """Create a new group sale"""
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
        return RedirectResponse("/groups", status_code=status.HTTP_303_SEE_OTHER)
    
    try:
        # Parse scheduled date
        scheduled_dt = None
        if scheduled_date:
            try:
                scheduled_dt = datetime.fromisoformat(scheduled_date)
            except ValueError:
                pass
        
        # Create order
        order = Order(
            user_id=user["id"],
            channel="grupo",
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
        
        # Create group metadata
        group = Group(
            order_id=order.id,
            visit_type=visit_type,
            has_oficio=has_oficio,
            institution_name=institution_name,
            responsible_name=responsible_name,
            state=state.upper() if state else None,
            city=city,
            ies_municipio=ies_municipio,
            scheduled_date=scheduled_dt,
            total_students=total_students,
            total_teachers=total_teachers
        )
        db.add(group)
        
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
            detail=f"Erro ao criar grupo: {str(e)}"
        )
