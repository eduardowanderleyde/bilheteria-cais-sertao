"""Dashboard routes"""
from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc
from datetime import datetime, date
from ..db import get_db
from ..models import Order, OrderItem, User
from ..auth import require_auth, get_user_info

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/api/test")
async def test_api():
    """Teste simples da API"""
    return {"status": "ok", "message": "API funcionando"}

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

@router.get("/api/reports/summary")
async def get_reports_summary(request: Request, db: Session = Depends(get_db)):
    """API para resumo das vendas (usado pelo dashboard)"""
    # Verifica se o usuário está autenticado, mas não falha se não estiver
    user = get_user_info(request)
    if not user.get("username"):
        return JSONResponse(content={"error": "Unauthorized"}, status_code=401)
    
    # Query para resumo dos últimos 30 dias
    results = db.query(
        func.date(Order.created_at).label('dia'),
        func.sum(OrderItem.qty).label('ingressos'),
        func.sum(OrderItem.qty * OrderItem.unit_price_cents).label('total_reais')
    ).join(OrderItem).filter(
        Order.deleted_at.is_(None)
    ).group_by(func.date(Order.created_at)).order_by(desc('dia')).limit(30).all()
    
    # Converter para formato esperado pelo frontend
    data = []
    for result in results:
        # Verificar se result.dia é string ou date
        if hasattr(result.dia, 'strftime'):
            dia_str = result.dia.strftime("%Y-%m-%d")
        else:
            dia_str = str(result.dia)
        
        data.append({
            "dia": dia_str,
            "ingressos": result.ingressos or 0,
            "total_reais": round((result.total_reais or 0) / 100, 2)
        })
    
    return JSONResponse(content={
        "success": True,
        "data": data
    })

@router.get("/api/dashboard/summary", response_class=HTMLResponse)
async def get_dashboard_summary_html(request: Request, db: Session = Depends(get_db)):
    """API para resumo das vendas em HTML"""
    try:
        # Query para resumo dos últimos 7 dias
        results = db.query(
            func.date(Order.created_at).label('dia'),
            func.sum(OrderItem.qty).label('ingressos'),
            func.sum(OrderItem.qty * OrderItem.unit_price_cents).label('total_reais')
        ).join(OrderItem).filter(
            Order.deleted_at.is_(None)
        ).group_by(func.date(Order.created_at)).order_by(desc('dia')).limit(7).all()
        
        # Gerar HTML
        if not results:
            return "<div class='text-center py-8 text-gray-500'>Nenhuma venda registrada nos últimos 7 dias</div>"
        
        html = "<div class='grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-7 gap-4'>"
        for result in results:
            # Converter dia para string se necessário
            if hasattr(result.dia, 'strftime'):
                dia = result.dia.strftime("%d/%m")
            else:
                dia = str(result.dia)[5:10]  # Pega dd/mm do formato YYYY-MM-DD
            ingressos = result.ingressos or 0
            total_reais = round((result.total_reais or 0) / 100, 2)
            
            html += f"""
            <div class='bg-slate-50 rounded-lg p-3 text-center'>
                <div class='text-xs text-slate-500 mb-1'>{dia}</div>
                <div class='text-lg font-bold'>{ingressos}</div>
                <div class='text-xs text-slate-600'>ingressos</div>
                <div class='text-sm font-semibold text-green-600'>R$ {total_reais:.2f}</div>
            </div>
            """
        html += "</div>"
        
        return html
        
    except Exception as e:
        return f"<div class='text-red-500 text-center py-8'>Erro: {str(e)}</div>"
