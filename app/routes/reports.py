"""Reports routes"""
from fastapi import APIRouter, Request, Depends, Query, HTTPException, status
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc
from datetime import datetime, date, timedelta
from typing import Optional
import pandas as pd
import tempfile
import os
from ..db import get_db
from ..models import Order, OrderItem, Group
from ..auth import require_auth, get_user_info, can_export

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/reports", response_class=HTMLResponse)
async def reports_page(request: Request):
    """Reports page"""
    user = require_auth(request)
    
    return templates.TemplateResponse("reports.html", {
        "request": request,
        "user": get_user_info(request)
    })

@router.get("/reports/by-state")
async def report_by_state(
    request: Request,
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Report by state (CSV)"""
    user = require_auth(request)
    
    if not can_export(user["role"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    # Parse dates
    start_dt = datetime.strptime(start_date, "%Y-%m-%d").date() if start_date else date.today() - timedelta(days=30)
    end_dt = datetime.strptime(end_date, "%Y-%m-%d").date() if end_date else date.today()
    
    # Query data
    results = db.query(
        Order.state,
        func.sum(OrderItem.qty).label('total_people'),
        func.sum(OrderItem.qty * OrderItem.unit_price_cents).label('total_revenue')
    ).join(OrderItem).filter(
        and_(
            func.date(Order.created_at) >= start_dt,
            func.date(Order.created_at) <= end_dt,
            Order.deleted_at.is_(None)
        )
    ).group_by(Order.state).order_by(desc('total_people')).all()
    
    # Create DataFrame
    df = pd.DataFrame([
        {
            'UF': result.state or 'Não informado',
            'Pessoas': result.total_people,
            'Receita (R$)': round(result.total_revenue / 100, 2)
        }
        for result in results
    ])
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as tmp:
        df.to_csv(tmp.name, index=False, encoding='utf-8')
        tmp_path = tmp.name
    
    return FileResponse(
        tmp_path,
        filename=f"pessoas_por_uf_{start_dt}_{end_dt}.csv",
        media_type="text/csv"
    )

@router.get("/reports/by-discount-reason")
async def report_by_discount_reason(
    request: Request,
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Report by discount reason (CSV)"""
    user = require_auth(request)
    
    if not can_export(user["role"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    # Parse dates
    start_dt = datetime.strptime(start_date, "%Y-%m-%d").date() if start_date else date.today() - timedelta(days=30)
    end_dt = datetime.strptime(end_date, "%Y-%m-%d").date() if end_date else date.today()
    
    # Query data
    results = db.query(
        OrderItem.discount_reason,
        func.sum(OrderItem.qty).label('count'),
        func.sum(OrderItem.qty * OrderItem.unit_price_cents).label('total_revenue')
    ).join(Order).filter(
        and_(
            func.date(Order.created_at) >= start_dt,
            func.date(Order.created_at) <= end_dt,
            Order.deleted_at.is_(None),
            OrderItem.discount_reason.isnot(None)
        )
    ).group_by(OrderItem.discount_reason).order_by(desc('count')).all()
    
    # Create DataFrame
    df = pd.DataFrame([
        {
            'Motivo': result.discount_reason or 'Não informado',
            'Quantidade': result.count,
            'Receita (R$)': round(result.total_revenue / 100, 2)
        }
        for result in results
    ])
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as tmp:
        df.to_csv(tmp.name, index=False, encoding='utf-8')
        tmp_path = tmp.name
    
    return FileResponse(
        tmp_path,
        filename=f"motivos_desconto_{start_dt}_{end_dt}.csv",
        media_type="text/csv"
    )

@router.get("/reports/by-payment-method")
async def report_by_payment_method(
    request: Request,
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Report by payment method (CSV)"""
    user = require_auth(request)
    
    if not can_export(user["role"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    # Parse dates
    start_dt = datetime.strptime(start_date, "%Y-%m-%d").date() if start_date else date.today() - timedelta(days=30)
    end_dt = datetime.strptime(end_date, "%Y-%m-%d").date() if end_date else date.today()
    
    # Query data
    results = db.query(
        Order.payment_method,
        func.sum(OrderItem.qty).label('count'),
        func.sum(OrderItem.qty * OrderItem.unit_price_cents).label('total_revenue')
    ).join(OrderItem).filter(
        and_(
            func.date(Order.created_at) >= start_dt,
            func.date(Order.created_at) <= end_dt,
            Order.deleted_at.is_(None)
        )
    ).group_by(Order.payment_method).order_by(desc('total_revenue')).all()
    
    # Create DataFrame
    df = pd.DataFrame([
        {
            'Forma de Pagamento': result.payment_method,
            'Quantidade': result.count,
            'Receita (R$)': round(result.total_revenue / 100, 2)
        }
        for result in results
    ])
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as tmp:
        df.to_csv(tmp.name, index=False, encoding='utf-8')
        tmp_path = tmp.name
    
    return FileResponse(
        tmp_path,
        filename=f"formas_pagamento_{start_dt}_{end_dt}.csv",
        media_type="text/csv"
    )

@router.get("/reports/daily")
async def daily_report(
    request: Request,
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Daily report (Excel)"""
    user = require_auth(request)
    
    if not can_export(user["role"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    # Parse dates
    start_dt = datetime.strptime(start_date, "%Y-%m-%d").date() if start_date else date.today() - timedelta(days=30)
    end_dt = datetime.strptime(end_date, "%Y-%m-%d").date() if end_date else date.today()
    
    # Query daily data
    daily_results = db.query(
        func.date(Order.created_at).label('date'),
        func.sum(OrderItem.qty).label('total_people'),
        func.sum(OrderItem.qty * OrderItem.unit_price_cents).label('total_revenue')
    ).join(OrderItem).filter(
        and_(
            func.date(Order.created_at) >= start_dt,
            func.date(Order.created_at) <= end_dt,
            Order.deleted_at.is_(None)
        )
    ).group_by(func.date(Order.created_at)).order_by('date').all()
    
    # Query by ticket type
    type_results = db.query(
        func.date(Order.created_at).label('date'),
        OrderItem.ticket_type,
        func.sum(OrderItem.qty).label('count')
    ).join(Order).filter(
        and_(
            func.date(Order.created_at) >= start_dt,
            func.date(Order.created_at) <= end_dt,
            Order.deleted_at.is_(None)
        )
    ).group_by(func.date(Order.created_at), OrderItem.ticket_type).all()
    
    # Query by payment method
    payment_results = db.query(
        func.date(Order.created_at).label('date'),
        Order.payment_method,
        func.sum(OrderItem.qty).label('count')
    ).join(OrderItem).filter(
        and_(
            func.date(Order.created_at) >= start_dt,
            func.date(Order.created_at) <= end_dt,
            Order.deleted_at.is_(None)
        )
    ).group_by(func.date(Order.created_at), Order.payment_method).all()
    
    # Create DataFrames
    daily_df = pd.DataFrame([
        {
            'Data': result.date,
            'Pessoas': result.total_people,
            'Receita (R$)': round(result.total_revenue / 100, 2)
        }
        for result in daily_results
    ])
    
    type_df = pd.DataFrame([
        {
            'Data': result.date,
            'Tipo': result.ticket_type,
            'Quantidade': result.count
        }
        for result in type_results
    ])
    
    payment_df = pd.DataFrame([
        {
            'Data': result.date,
            'Forma de Pagamento': result.payment_method,
            'Quantidade': result.count
        }
        for result in payment_results
    ])
    
    # Create Excel file
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
        with pd.ExcelWriter(tmp.name, engine='openpyxl') as writer:
            daily_df.to_excel(writer, sheet_name='Resumo_Diario', index=False)
            type_df.to_excel(writer, sheet_name='Por_Tipo', index=False)
            payment_df.to_excel(writer, sheet_name='Por_Pagamento', index=False)
        tmp_path = tmp.name
    
    return FileResponse(
        tmp_path,
        filename=f"relatorio_diario_{start_dt}_{end_dt}.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
