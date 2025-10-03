"""Reports routes"""
from fastapi import APIRouter, Request, Depends, Query, HTTPException, status
from fastapi.responses import HTMLResponse, FileResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc
from datetime import datetime, date, timedelta
from typing import Optional
import pandas as pd
import tempfile
import os
from ..db import get_db
from ..models import Order, OrderItem, Group, GroupVisit
from ..auth import require_auth, get_user_info, can_export

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
async def reports_page(request: Request):
    """Reports page"""
    user = require_auth(request)
    
    return templates.TemplateResponse("reports.html", {
        "request": request,
        "user": get_user_info(request)
    })

@router.get("/by-state")
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

@router.get("/by-discount-reason")
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

@router.get("/by-payment-method")
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

@router.get("/by-payment.csv")
async def report_by_payment_csv(
    request: Request,
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Export payment method report as CSV"""
    user = require_auth(request)
    
    # Parse dates
    start = None
    end = None
    if start_date:
        start = datetime.strptime(start_date, "%Y-%m-%d").date()
    if end_date:
        end = datetime.strptime(end_date, "%Y-%m-%d").date()
    
    # Build query
    query = db.query(
        Order.payment_method,
        func.count(Order.id).label("qtd"),
        func.sum(OrderItem.qty * OrderItem.unit_price_cents).label("total_cents")
    ).join(OrderItem).filter(Order.deleted_at.is_(None))
    
    if start:
        query = query.filter(func.date(Order.created_at) >= start)
    if end:
        query = query.filter(func.date(Order.created_at) <= end)
    
    results = query.group_by(Order.payment_method).all()
    
    # Create DataFrame
    data = []
    for result in results:
        data.append({
            "forma_pagamento": result.payment_method,
            "quantidade_vendas": result.qtd,
            "receita_total": round((result.total_cents or 0) / 100, 2)
        })
    
    df = pd.DataFrame(data)
    
    # Create temporary file
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".csv", mode='w', encoding='utf-8')
    df.to_csv(tmp.name, index=False)
    tmp.close()
    
    return FileResponse(
        tmp.name,
        filename="vendas_por_pagamento.csv",
        media_type="text/csv"
    )

@router.get("/daily")
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

# Group reports endpoints
def _period_days(days: int):
    start = date.today() - timedelta(days=days)
    return start, date.today()

@router.get("/api/groups/weekly")
def groups_weekly(db: Session = Depends(get_db), weeks: int = 8):
    """Weekly groups report"""
    # Cap maximum weeks
    weeks = min(weeks, 52)  # Max 1 year
    
    start = date.today() - timedelta(days=7*weeks)
    
    # Use SQLite strftime for compatibility
    q = (db.query(
            func.strftime('%Y-%W', GroupVisit.date).label('year_week'),
            func.count(GroupVisit.id).label('groups'),
            func.coalesce(func.sum(GroupVisit.size), 0).label('people')
         )
         .filter(GroupVisit.date >= start)
         .group_by(func.strftime('%Y-%W', GroupVisit.date))
         .order_by(func.strftime('%Y-%W', GroupVisit.date)))
    
    return [{"bucket": r[0], "groups": int(r[1]), "people": int(r[2])} for r in q.all()]

@router.get("/api/groups/monthly")
def groups_monthly(db: Session = Depends(get_db), months: int = 12):
    """Monthly groups report"""
    # Cap maximum months
    months = min(months, 24)  # Max 2 years
    
    start = date.today().replace(day=1) - timedelta(days=30*months)
    
    # Use SQLite strftime for compatibility (PostgreSQL would use date_trunc)
    q = (db.query(
            func.strftime('%Y-%m', GroupVisit.date).label('ym'),
            func.count(GroupVisit.id).label('groups'),
            func.coalesce(func.sum(GroupVisit.size), 0).label('people')
         )
         .filter(GroupVisit.date >= start)
         .group_by(func.strftime('%Y-%m', GroupVisit.date))
         .order_by(func.strftime('%Y-%m', GroupVisit.date)))
    
    return [{"month": r[0], "groups": int(r[1]), "people": int(r[2])} for r in q.all()]

@router.get("/api/groups/top-origins")
def groups_top_origins(db: Session = Depends(get_db), days: int = 180, limit: int = 10):
    """Top origins for groups"""
    # Cap maximum values
    days = min(days, 365)  # Max 1 year
    limit = min(limit, 100)  # Max 100 results
    
    start, _ = _period_days(days)
    q = (db.query(GroupVisit.state, GroupVisit.city,
                  func.count(GroupVisit.id).label('groups'),
                  func.coalesce(func.sum(GroupVisit.size), 0).label('people'))
           .filter(GroupVisit.date >= start)
           .group_by(GroupVisit.state, GroupVisit.city)
           .order_by(desc('people')).limit(limit))
    return [{"state": s or "", "city": c or "", "groups": int(g), "people": int(p)} for s,c,g,p in q.all()]

@router.get("/api/groups/kpis")
def groups_kpis(db: Session = Depends(get_db), days: int = 30):
    """Groups KPIs"""
    # Cap maximum days
    days = min(days, 365)  # Max 1 year
    
    start, _ = _period_days(days)
    
    # Single query for all KPIs (more efficient)
    result = db.query(
        func.count(GroupVisit.id).label('groups'),
        func.coalesce(func.sum(GroupVisit.size), 0).label('people'),
        func.count(func.distinct(GroupVisit.date)).label('days_with')
    ).filter(GroupVisit.date >= start).first()
    
    return {
        "groups": int(result.groups or 0), 
        "people": int(result.people or 0), 
        "days_with": int(result.days_with or 0)
    }

@router.get("/groups/export.xlsx")
def groups_export(db: Session = Depends(get_db), months: int = 12):
    """Export groups to Excel with multiple sheets"""
    # Cap maximum months
    months = min(months, 24)  # Max 2 years
    
    start_date = date.today().replace(day=1) - timedelta(days=30*months)
    
    # 1) Raw data (limit to prevent memory issues)
    rows = (db.query(GroupVisit.date, GroupVisit.institution, GroupVisit.size,
                     GroupVisit.state, GroupVisit.city, GroupVisit.scheduled, GroupVisit.price_total)
              .filter(GroupVisit.date >= start_date)
              .order_by(GroupVisit.date.desc())
              .limit(10000)  # Cap at 10k records
              .all())
    df_raw = pd.DataFrame(rows, columns=["Data","Instituição","Pessoas","UF","Cidade","Agendada","ValorTotal"])

    # 2) Monthly aggregation (SQL-based for performance)
    monthly_rows = (db.query(
        func.strftime('%Y-%m', GroupVisit.date).label('month'),
        func.count(GroupVisit.id).label('grupos'),
        func.coalesce(func.sum(GroupVisit.size), 0).label('pessoas'),
        func.coalesce(func.sum(GroupVisit.price_total), 0).label('valor_total')
    )
    .filter(GroupVisit.date >= start_date)
    .group_by(func.strftime('%Y-%m', GroupVisit.date))
    .order_by(func.strftime('%Y-%m', GroupVisit.date))
    .all())
    
    df_month = pd.DataFrame(monthly_rows, columns=["Mês", "Grupos", "Pessoas", "ValorTotal"])

    # 3) Weekly aggregation (SQL-based)
    weekly_rows = (db.query(
        func.strftime('%Y-%W', GroupVisit.date).label('week'),
        func.count(GroupVisit.id).label('grupos'),
        func.coalesce(func.sum(GroupVisit.size), 0).label('pessoas'),
        func.coalesce(func.sum(GroupVisit.price_total), 0).label('valor_total')
    )
    .filter(GroupVisit.date >= start_date)
    .group_by(func.strftime('%Y-%W', GroupVisit.date))
    .order_by(func.strftime('%Y-%W', GroupVisit.date))
    .all())
    
    df_week = pd.DataFrame(weekly_rows, columns=["Semana", "Grupos", "Pessoas", "ValorTotal"])

    # 4) Top origins (SQL-based)
    origin_rows = (db.query(
        GroupVisit.state.label('uf'),
        GroupVisit.city.label('cidade'),
        func.count(GroupVisit.id).label('grupos'),
        func.coalesce(func.sum(GroupVisit.size), 0).label('pessoas')
    )
    .filter(GroupVisit.date >= start_date)
    .group_by(GroupVisit.state, GroupVisit.city)
    .order_by(desc('pessoas'))
    .limit(50)
    .all())
    
    df_origin = pd.DataFrame(origin_rows, columns=["UF", "Cidade", "Grupos", "Pessoas"])

    # Create Excel file
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
    with pd.ExcelWriter(tmp.name, engine="openpyxl") as xw:
        df_raw.to_excel(xw, index=False, sheet_name="Bruto")
        df_month.to_excel(xw, index=False, sheet_name="Mensal")
        df_week.to_excel(xw, index=False, sheet_name="Semanal")
        df_origin.to_excel(xw, index=False, sheet_name="TopOrigens")

    return FileResponse(
        tmp.name, 
        filename="Relatorio_Grupos.xlsx", 
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

@router.get("/groups/export.csv")
def groups_export_csv(db: Session = Depends(get_db), months: int = 12):
    """Export groups to CSV (streaming for large datasets)"""
    # Cap maximum months
    months = min(months, 24)  # Max 2 years
    
    start_date = date.today().replace(day=1) - timedelta(days=30*months)
    
    def generate_csv():
        """Generator for CSV data"""
        # Header
        yield "Data,Instituição,Pessoas,UF,Cidade,Agendada,ValorTotal\n"
        
        # Data rows (streaming)
        query = (db.query(GroupVisit.date, GroupVisit.institution, GroupVisit.size,
                         GroupVisit.state, GroupVisit.city, GroupVisit.scheduled, GroupVisit.price_total)
                  .filter(GroupVisit.date >= start_date)
                  .order_by(GroupVisit.date.desc())
                  .yield_per(1000))  # Process in chunks
        
        for row in query:
            # Escape CSV values
            date_str = row.date.strftime("%Y-%m-%d") if row.date else ""
            institution = str(row.institution or "").replace(",", ";").replace("\n", " ")
            size = str(row.size or 0)
            state = str(row.state or "")
            city = str(row.city or "").replace(",", ";").replace("\n", " ")
            scheduled = "Sim" if row.scheduled else "Não"
            price = str(row.price_total or 0)
            
            yield f"{date_str},{institution},{size},{state},{city},{scheduled},{price}\n"
    
    return StreamingResponse(
        generate_csv(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=grupos.csv"}
    )
