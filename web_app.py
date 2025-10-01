# web_app.py
# Sistema de Bilheteria - Versão Web com FastAPI + HTMX
# Museu Cais do Sertão

from fastapi import FastAPI, Request, Form, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
import sqlite3
import bcrypt
import pandas as pd
from datetime import datetime, date
import os
import json
from typing import Optional
import uvicorn

app = FastAPI(title="Bilheteria - Museu Cais do Sertão", version="1.0.0")
app.add_middleware(SessionMiddleware, secret_key="bilheteria-cais-secret-key-2024")

# Configuração de templates e arquivos estáticos
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Banco de dados
DB = "bilheteria.db"

# Chave da sessão
SESSION_KEY = "session_user"

def init_db():
    """Inicializa o banco de dados SQLite"""
    con = sqlite3.connect(DB)
    cur = con.cursor()
    
    # Ativa WAL mode
    cur.execute("PRAGMA journal_mode=WAL;")
    
    # Tabela de usuários
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE,
            password_hash BLOB,
            role TEXT
        );
    """)
    
    # Tabela de vendas
    cur.execute("""
        CREATE TABLE IF NOT EXISTS sales(
            id INTEGER PRIMARY KEY,
            sold_at TEXT,
            ticket_type TEXT,
            qty INTEGER,
            unit_price_cents INTEGER,
            operator_username TEXT,
            name TEXT,
            state TEXT,
            city TEXT,
            note TEXT
        );
    """)
    
    # Índices
    cur.execute("CREATE INDEX IF NOT EXISTS idx_sales_date ON sales(sold_at);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_sales_type ON sales(ticket_type);")
    
    # Usuário padrão
    cur.execute("SELECT 1 FROM users WHERE username='funcionario1'")
    if not cur.fetchone():
        pwd = b"123456"
        cur.execute("INSERT INTO users(username,password_hash,role) VALUES (?,?,?)",
                    ("funcionario1", bcrypt.hashpw(pwd, bcrypt.gensalt()), "operator"))
    
    con.commit()
    con.close()

def current_user(request: Request):
    """Retorna o usuário atual da sessão"""
    return request.session.get(SESSION_KEY)

def price_for(ticket_type: str) -> int:
    """Retorna o preço em centavos para o tipo de ingresso"""
    prices = {"inteira": 1000, "meia": 500, "gratuita": 0}
    return prices.get(ticket_type, 0)

@app.on_event("startup")
async def startup_event():
    """Inicializa o banco de dados na startup"""
    init_db()

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    """Página inicial - redireciona para login ou dashboard"""
    if not current_user(request):
        return RedirectResponse("/login")
    return RedirectResponse("/dashboard")

@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    """Página de login"""
    return templates.TemplateResponse(
        "login.html",
        {"request": request, "no_sidebar": True, "error": None}
    )

@app.post("/login")
def login(request: Request, username: str = Form(...), password: str = Form(...)):
    """Processa o login"""
    con = sqlite3.connect(DB)
    cur = con.cursor()
    cur.execute("SELECT password_hash, role FROM users WHERE username=?", (username,))
    row = cur.fetchone()
    con.close()

    if row and bcrypt.checkpw(password.encode(), row[0]):
        request.session[SESSION_KEY] = username
        return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)
    else:
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "no_sidebar": True, "error": "Usuário/senha inválidos"},
            status_code=400
        )

@app.get("/logout")
def logout(request: Request):
    """Logout do usuário"""
    request.session.pop(SESSION_KEY, None)
    return RedirectResponse("/login", status_code=status.HTTP_303_SEE_OTHER)

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    """Dashboard principal"""
    if not current_user(request):
        return RedirectResponse("/login")
    
    user = current_user(request)
    
    # Busca dados do dia atual
    today = datetime.now().strftime('%Y-%m-%d')
    con = sqlite3.connect(DB)
    cur = con.cursor()
    
    # Total de ingressos hoje
    cur.execute("SELECT SUM(qty) FROM sales WHERE date(sold_at) = ?", (today,))
    ingressos_hoje = cur.fetchone()[0] or 0
    
    # Receita hoje
    cur.execute("SELECT SUM(qty * unit_price_cents) FROM sales WHERE date(sold_at) = ?", (today,))
    receita_hoje = (cur.fetchone()[0] or 0) / 100
    
    # Inteiras hoje
    cur.execute("SELECT SUM(qty) FROM sales WHERE date(sold_at) = ? AND ticket_type = 'inteira'", (today,))
    inteiras_hoje = cur.fetchone()[0] or 0
    
    # Meias hoje
    cur.execute("SELECT SUM(qty) FROM sales WHERE date(sold_at) = ? AND ticket_type = 'meia'", (today,))
    meias_hoje = cur.fetchone()[0] or 0
    
    # Gratuitas hoje
    cur.execute("SELECT SUM(qty) FROM sales WHERE date(sold_at) = ? AND ticket_type = 'gratuita'", (today,))
    gratuitas_hoje = cur.fetchone()[0] or 0
    
    # Vendas recentes do dia (últimas 10)
    cur.execute("""
        SELECT id, ticket_type, qty, unit_price_cents, name, sold_at 
        FROM sales 
        WHERE date(sold_at) = ? 
        ORDER BY sold_at DESC 
        LIMIT 10
    """, (today,))
    vendas_recentes = cur.fetchall()
    
    con.close()
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request, 
        "user": {"username": user},
        "ingressos_hoje": ingressos_hoje,
        "receita_hoje": f"{receita_hoje:.2f}",
        "inteiras_hoje": inteiras_hoje,
        "meias_hoje": meias_hoje,
        "gratuitas_hoje": gratuitas_hoje,
        "vendas_recentes": vendas_recentes
    })

@app.get("/sell", response_class=HTMLResponse)
def sell_page(request: Request):
    """Página de vendas"""
    if not current_user(request):
        return RedirectResponse("/login")
    
    user = current_user(request)
    return templates.TemplateResponse("sell.html", {
        "request": request,
        "user": {"username": user}
    })

@app.post("/sell")
def sell_post(
    request: Request,
    qtd_inteira: int = Form(0),
    qtd_meia: int = Form(0),
    qtd_gratuita: int = Form(0),
    name: Optional[str] = Form(None),
    state: Optional[str] = Form(None),
    city: Optional[str] = Form(None),
    note: Optional[str] = Form(None)
):
    """Registra venda com tipos mistos"""
    if not current_user(request):
        return RedirectResponse("/login", status_code=303)
    
    user = current_user(request)
    
    # Define os itens com quantidades e preços
    items = [
        ("inteira", qtd_inteira, 1000),
        ("meia", qtd_meia, 500),
        ("gratuita", qtd_gratuita, 0),
    ]
    
    # Verifica se pelo menos um item foi selecionado
    if sum(q for _, q, _ in items) <= 0:
        return RedirectResponse("/sell", status_code=303)
    
    try:
        con = sqlite3.connect(DB)
        cur = con.cursor()
        
        # Insere uma linha para cada tipo com quantidade > 0
        now = datetime.now().isoformat()
        for tipo, qtd, preco in items:
            if qtd and qtd > 0:
                cur.execute("""
                    INSERT INTO sales(sold_at, ticket_type, qty, unit_price_cents, operator_username, name, state, city, note)
                    VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (now, tipo, qtd, preco, user, name, state, city, note))
        
        con.commit()
        con.close()
        
        return RedirectResponse("/dashboard", status_code=303)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao salvar venda: {str(e)}")

@app.post("/delete_sale/{sale_id}")
def delete_sale(request: Request, sale_id: int):
    """Exclui uma venda (apenas no mesmo dia)"""
    if not current_user(request):
        return RedirectResponse("/login", status_code=303)
    
    try:
        con = sqlite3.connect(DB)
        cur = con.cursor()
        
        # Verifica se a venda existe e é do dia atual
        today = datetime.now().strftime('%Y-%m-%d')
        cur.execute("""
            SELECT id, sold_at FROM sales 
            WHERE id = ? AND date(sold_at) = ?
        """, (sale_id, today))
        
        sale = cur.fetchone()
        if not sale:
            con.close()
            raise HTTPException(status_code=404, detail="Venda não encontrada ou não pode ser excluída")
        
        # Exclui a venda
        cur.execute("DELETE FROM sales WHERE id = ?", (sale_id,))
        con.commit()
        con.close()
        
        return RedirectResponse("/reports", status_code=303)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao excluir venda: {str(e)}")

@app.post("/api/sell")
async def register_sale(
    request: Request,
    ticket_type: str = Form(...),
    qty: int = Form(...),
    name: Optional[str] = Form(None),
    state: Optional[str] = Form(None),
    city: Optional[str] = Form(None),
    note: Optional[str] = Form(None)
):
    """Registra uma nova venda"""
    try:
        if not current_user(request):
            return {"success": False, "message": "Não autenticado"}
        
        user = current_user(request)
        if qty <= 0:
            raise HTTPException(status_code=400, detail="Quantidade deve ser maior que zero")
        
        con = sqlite3.connect(DB)
        cur = con.cursor()
        cur.execute("""INSERT INTO sales(sold_at,ticket_type,qty,unit_price_cents,operator_username,name,state,city,note)
                       VALUES(?,?,?,?,?,?,?,?,?)""",
                    (datetime.now().isoformat(), ticket_type, qty, price_for(ticket_type), 
                     user, name, state, city, note))
        con.commit()
        con.close()
        
        return {
            "success": True, 
            "message": f"Venda registrada! {qty} ingresso(s) {ticket_type} - R$ {qty * price_for(ticket_type) / 100:.2f}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao salvar venda: {str(e)}")

@app.get("/reports", response_class=HTMLResponse)
def reports_page(request: Request):
    """Página de relatórios"""
    if not current_user(request):
        return RedirectResponse("/login")
    
    user = current_user(request)
    return templates.TemplateResponse("reports.html", {
        "request": request,
        "user": {"username": user}
    })

@app.get("/api/reports/summary")
def get_reports_summary(request: Request):
    """Retorna resumo das vendas"""
    if not current_user(request):
        raise HTTPException(status_code=401, detail="Não autenticado")
    
    try:
        con = sqlite3.connect(DB)
        df = pd.read_sql_query("""
            SELECT date(sold_at) AS dia,
                   SUM(qty) AS ingressos,
                   ROUND(SUM(qty*unit_price_cents)/100.0, 2) AS total_reais
            FROM sales
            GROUP BY dia
            ORDER BY dia DESC
            LIMIT 30;
        """, con)
        con.close()
        
        data = df.to_dict("records")
        
        # Se for requisição HTMX, retorna HTML
        if request.headers.get("hx-request"):
            return templates.TemplateResponse("reports_summary.html", {
                "request": request,
                "data": data
            })
        
        # Senão, retorna JSON
        return {
            "success": True,
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao carregar relatórios: {str(e)}")

@app.get("/api/reports/export")
def export_reports(request: Request):
    """Exporta relatório para Excel"""
    if not current_user(request):
        raise HTTPException(status_code=401, detail="Não autenticado")
    
    try:
        con = sqlite3.connect(DB)
        df = pd.read_sql_query("""
            SELECT date(sold_at) AS dia,
                   ticket_type AS tipo,
                   SUM(qty) AS quantidade,
                   ROUND(SUM(qty*unit_price_cents)/100.0, 2) AS total_reais
            FROM sales
            GROUP BY dia, ticket_type
            ORDER BY dia DESC, ticket_type;
        """, con)
        con.close()
        
        if df.empty:
            raise HTTPException(status_code=404, detail="Não há vendas para exportar")
        
        # Salva arquivo temporário
        filename = f"relatorio_vendas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        filepath = f"temp/{filename}"
        
        # Cria diretório temp se não existir
        os.makedirs("temp", exist_ok=True)
        
        df.to_excel(filepath, index=False)
        
        return FileResponse(
            path=filepath,
            filename=filename,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao exportar: {str(e)}")

@app.get("/logout")
async def logout(request: Request):
    """Logout do usuário"""
    session_id = request.cookies.get("session_id")
    if session_id in sessions:
        del sessions[session_id]
    
    response = RedirectResponse(url="/", status_code=302)
    response.delete_cookie(key="session_id")
    return response

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
