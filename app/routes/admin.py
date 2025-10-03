"""Admin routes"""
from fastapi import APIRouter, Request, Depends, Query, Form, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc
from datetime import datetime, date
from typing import Optional
from ..db import get_db
from ..models import Order, OrderItem, Group, OrderEvent, User
from ..auth import require_auth, get_user_info, can_view_admin, can_delete, can_edit, set_csrf_token

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/admin", response_class=HTMLResponse)
async def admin_home(request: Request):
    """Admin home page"""
    user = require_auth(request)
    
    if not can_view_admin(user["role"]):
        return RedirectResponse("/unauthorized", status_code=status.HTTP_303_SEE_OTHER)
    
    return templates.TemplateResponse("admin_home.html", {
        "request": request,
        "user": get_user_info(request)
    })

@router.get("/admin/orders", response_class=HTMLResponse)
async def admin_orders(
    request: Request,
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
    q: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    db: Session = Depends(get_db)
):
    """Admin orders list"""
    user = require_auth(request)
    
    if not can_view_admin(user["role"]):
        return RedirectResponse("/unauthorized", status_code=status.HTTP_303_SEE_OTHER)
    
    # Pagination
    limit = 20
    offset = (page - 1) * limit
    
    # Build query
    query = db.query(Order).filter(Order.deleted_at.is_(None))
    
    # Apply filters
    if start_date:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d").date()
        query = query.filter(func.date(Order.created_at) >= start_dt)
    
    if end_date:
        end_dt = datetime.strptime(end_date, "%Y-%m-%d").date()
        query = query.filter(func.date(Order.created_at) <= end_dt)
    
    if state:
        query = query.filter(Order.state == state.upper())
    
    if q:
        query = query.filter(
            or_(
                Order.city.ilike(f"%{q}%"),
                Order.note.ilike(f"%{q}%")
            )
        )
    
    # Get total count
    total = query.count()
    
    # Get orders with pagination
    orders = query.order_by(desc(Order.created_at)).offset(offset).limit(limit).all()
    
    # Calculate pagination info
    total_pages = (total + limit - 1) // limit
    
    return templates.TemplateResponse("admin_orders.html", {
        "request": request,
        "user": get_user_info(request),
        "orders": orders,
        "start_date": start_date,
        "end_date": end_date,
        "state": state,
        "q": q,
        "page": page,
        "total_pages": total_pages,
        "has_prev": page > 1,
        "has_next": page < total_pages
    })

@router.get("/admin/groups", response_class=HTMLResponse)
async def admin_groups(
    request: Request,
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
    q: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    db: Session = Depends(get_db)
):
    """Admin groups list"""
    user = require_auth(request)
    
    if not can_view_admin(user["role"]):
        return RedirectResponse("/unauthorized", status_code=status.HTTP_303_SEE_OTHER)
    
    # Pagination
    limit = 20
    offset = (page - 1) * limit
    
    # Build query
    query = db.query(Group).join(Order).filter(Order.deleted_at.is_(None))
    
    # Apply filters
    if start_date:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d").date()
        query = query.filter(func.date(Order.created_at) >= start_dt)
    
    if end_date:
        end_dt = datetime.strptime(end_date, "%Y-%m-%d").date()
        query = query.filter(func.date(Order.created_at) <= end_dt)
    
    if state:
        query = query.filter(Group.state == state.upper())
    
    if q:
        query = query.filter(
            or_(
                Group.institution_name.ilike(f"%{q}%"),
                Group.responsible_name.ilike(f"%{q}%"),
                Group.city.ilike(f"%{q}%")
            )
        )
    
    # Get total count
    total = query.count()
    
    # Get groups with pagination
    groups = query.order_by(desc(Order.created_at)).offset(offset).limit(limit).all()
    
    # Calculate pagination info
    total_pages = (total + limit - 1) // limit
    
    return templates.TemplateResponse("admin_groups.html", {
        "request": request,
        "user": get_user_info(request),
        "groups": groups,
        "start_date": start_date,
        "end_date": end_date,
        "state": state,
        "q": q,
        "page": page,
        "total_pages": total_pages,
        "has_prev": page > 1,
        "has_next": page < total_pages
    })

@router.post("/admin/orders/{order_id}/delete")
async def admin_delete_order(
    order_id: int,
    request: Request,
    reason: str = Form(""),
    db: Session = Depends(get_db)
):
    """Admin delete order"""
    user = require_auth(request)
    
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
        return RedirectResponse("/admin/orders", status_code=status.HTTP_303_SEE_OTHER)
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao excluir pedido: {str(e)}"
        )

@router.post("/admin/groups/{group_id}/delete")
async def admin_delete_group(
    group_id: int,
    request: Request,
    reason: str = Form(""),
    db: Session = Depends(get_db)
):
    """Admin delete group"""
    user = require_auth(request)
    
    if not can_delete(user["role"]):
        return RedirectResponse("/unauthorized", status_code=status.HTTP_303_SEE_OTHER)
    
    # Get group and its order
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grupo não encontrado"
        )
    
    order = group.order
    if order.deleted_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Pedido já foi excluído"
        )
    
    try:
        # Soft delete the order (which will affect the group)
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
        return RedirectResponse("/admin/groups", status_code=status.HTTP_303_SEE_OTHER)
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao excluir grupo: {str(e)}"
        )
