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

# Motivos para meia entrada
MEIA_REASONS = [
    "idoso",
    "professor_ins_particular", 
    "estudante_ins_particular",
    "pcd_acompanhante",
    "doador_sangue",
    "enfermagem"
]

# Motivos para gratuidade
GRAT_REASONS = [
    "estudante_rede_publica",
    "professor_ins_publica", 
    "guia_turismo",
    "crianca_0_5",
    "politica_gratuidade",
    "funcionario_museu",
    "policial_bombeiro_militar"
]

# Labels bonitas para os motivos
REASON_LABELS = {
    # Meia entrada
    "idoso": "Idoso (60+)",
    "professor_ins_particular": "Professor - Instituição Particular",
    "estudante_ins_particular": "Estudante - Instituição Particular", 
    "pcd_acompanhante": "PCD + Acompanhante",
    "doador_sangue": "Doador de Sangue",
    "enfermagem": "Profissional de Enfermagem",
    
    # Gratuidade
    "estudante_rede_publica": "Estudante - Rede Pública",
    "professor_ins_publica": "Professor - Instituição Pública",
    "guia_turismo": "Guia de Turismo",
    "crianca_0_5": "Criança 0-5 anos",
    "politica_gratuidade": "Política de Gratuidade",
    "funcionario_museu": "Funcionário do Museu",
    "policial_bombeiro_militar": "Policial/Bombeiro Militar"
}

def ensure_payment_method_column():
    """Garante que a coluna payment_method existe na tabela orders"""
    con = sqlite3.connect(DB)
    cur = con.cursor()
    cur.execute("PRAGMA table_info(orders);")
    cols = [r[1] for r in cur.fetchall()]
    if "payment_method" not in cols:
        cur.execute("ALTER TABLE orders ADD COLUMN payment_method TEXT;")
        con.commit()
    con.close()

def ensure_users():
    """Garante que os usuários padrão existem com os papéis corretos"""
    con = sqlite3.connect(DB)
    cur = con.cursor()
    
    # Verifica se a coluna is_active existe
    cur.execute("PRAGMA table_info(users);")
    cols = [r[1] for r in cur.fetchall()]
    if "is_active" not in cols:
        cur.execute("ALTER TABLE users ADD COLUMN is_active INTEGER NOT NULL DEFAULT 1;")
    
    # Função para criar/atualizar usuário
    def upsert_user(username, raw_password, role):
        # Verifica se usuário existe
        cur.execute("SELECT id FROM users WHERE username = ?", (username,))
        user_exists = cur.fetchone()
        
        # Hash da senha
        password_hash = bcrypt.hashpw(raw_password.encode(), bcrypt.gensalt())
        
        if user_exists:
            # Atualiza usuário existente
            cur.execute("""
                UPDATE users 
                SET password_hash = ?, role = ?, is_active = 1 
                WHERE username = ?
            """, (password_hash, role, username))
        else:
            # Cria novo usuário
            cur.execute("""
                INSERT INTO users(username, password_hash, role, is_active)
                VALUES(?, ?, ?, 1)
            """, (username, password_hash, role))
    
    # Cria/atualiza usuários padrão
    upsert_user("admingeral", "18091992123", "admin")
    upsert_user("keila", "Januario76", "gestora")
    upsert_user("Evelyn", "Januario76", "gestora")
    upsert_user("bilheteira1", "Januario72", "bilheteira")
    upsert_user("bilheteira2", "Januario72", "bilheteira")
    
    # Desativa funcionario1 antigo
    cur.execute("UPDATE users SET is_active = 0 WHERE username = 'funcionario1'")
    
    con.commit()
    con.close()

def init_db():
    """Inicializa o banco de dados SQLite com nova arquitetura"""
    con = sqlite3.connect(DB)
    cur = con.cursor()
    
    # Ativa WAL mode
    cur.execute("PRAGMA journal_mode=WAL;")
    
    # Tabela de usuários (atualizada com papéis e permissões)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE,
            password_hash BLOB,
            role TEXT NOT NULL DEFAULT 'bilheteira',
            is_active INTEGER NOT NULL DEFAULT 1
        );
    """)
    
    # NOVA ARQUITETURA: Tabela de pedidos (cabeçalho)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS orders(
            id INTEGER PRIMARY KEY,
            created_at TEXT NOT NULL,
            operator_username TEXT NOT NULL,
            channel TEXT NOT NULL DEFAULT 'balcao',
            state TEXT,
            city TEXT,
            note TEXT,
            deleted_at TEXT NULL
        );
    """)
    
    # NOVA ARQUITETURA: Tabela de itens do pedido
    cur.execute("""
        CREATE TABLE IF NOT EXISTS order_items(
            id INTEGER PRIMARY KEY,
            order_id INTEGER NOT NULL,
            ticket_type TEXT NOT NULL,
            qty INTEGER NOT NULL,
            unit_price_cents INTEGER NOT NULL,
            reason TEXT NULL,
            FOREIGN KEY (order_id) REFERENCES orders(id)
        );
    """)
    
    # NOVA ARQUITETURA: Tabela de grupos (metadados de visita em grupo)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS groups(
            id INTEGER PRIMARY KEY,
            order_id INTEGER NOT NULL,
            visit_type TEXT NOT NULL,
            has_oficio INTEGER NOT NULL DEFAULT 0,
            institution_name TEXT,
            total_students INTEGER DEFAULT 0,
            total_teachers INTEGER DEFAULT 0,
            responsible_name TEXT,
            state TEXT,
            city TEXT,
            ies_municipio TEXT,
            scheduled_date TEXT NULL,
            FOREIGN KEY (order_id) REFERENCES orders(id)
        );
    """)
    
    # NOVA ARQUITETURA: Tabela de auditoria (log de eventos)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS order_events(
            id INTEGER PRIMARY KEY,
            order_id INTEGER NOT NULL,
            action TEXT NOT NULL,
            who TEXT NOT NULL,
            when_created TEXT NOT NULL,
            reason TEXT NULL,
            FOREIGN KEY (order_id) REFERENCES orders(id)
        );
    """)
    
    # Tabela de vendas (legacy - mantida para compatibilidade)
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
    
    # Índices para performance
    cur.execute("CREATE INDEX IF NOT EXISTS idx_orders_created_at ON orders(created_at);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_orders_channel ON orders(channel);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_orders_state_city ON orders(state, city);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_items_order_id ON order_items(order_id);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_items_ticket_type ON order_items(ticket_type);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_groups_order_id ON groups(order_id);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_order_events_order_id ON order_events(order_id);")
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
    
    # Garante que a coluna payment_method existe
    ensure_payment_method_column()
    
    # Garante que os usuários padrão existem
    ensure_users()

def current_user(request: Request):
    """Retorna o usuário atual da sessão"""
    user_data = request.session.get(SESSION_KEY)
    if isinstance(user_data, dict):
        return user_data.get("username")
    return user_data

def require_role(request: Request, allowed_roles: set):
    """Verifica se o usuário atual tem um dos papéis permitidos"""
    user_data = request.session.get(SESSION_KEY)
    if isinstance(user_data, dict):
        return user_data.get("role") in allowed_roles
    return False

def get_user_info(request: Request):
    """Retorna informações completas do usuário atual"""
    user_data = request.session.get(SESSION_KEY)
    if isinstance(user_data, dict):
        return {
            "username": user_data.get("username"),
            "role": user_data.get("role")
        }
    return {"username": user_data}

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
    """Processa o login com verificação de papéis"""
    con = sqlite3.connect(DB)
    cur = con.cursor()
    cur.execute("SELECT password_hash, role FROM users WHERE username=? AND is_active=1", (username,))
    row = cur.fetchone()
    con.close()

    if row and bcrypt.checkpw(password.encode(), row[0]):
        # Salva informações completas do usuário na sessão
        request.session[SESSION_KEY] = {
            "username": username,
            "role": row[1]
        }
        return RedirectResponse("/dashboard", status_code=status.HTTP_303_SEE_OTHER)
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

@app.get("/unauthorized", response_class=HTMLResponse)
def unauthorized(request: Request):
    """Página de acesso negado"""
    return templates.TemplateResponse("unauthorized.html", {
        "request": request,
        "no_sidebar": True
    })

@app.get("/whoami", response_class=HTMLResponse)
def whoami(request: Request):
    """Mostra informações do usuário logado"""
    if not current_user(request):
        return RedirectResponse("/login", status_code=303)
    
    user_info = get_user_info(request)
    return templates.TemplateResponse("whoami.html", {
        "request": request,
        "no_sidebar": True,
        "user": user_info
    })

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    """Dashboard principal usando nova arquitetura"""
    if not current_user(request):
        return RedirectResponse("/login")
    
    user = current_user(request)
    
    # Busca dados do dia atual usando nova arquitetura
    today = datetime.now().strftime('%Y-%m-%d')
    con = sqlite3.connect(DB)
    cur = con.cursor()
    
    # Total de ingressos hoje (nova arquitetura)
    cur.execute("""
        SELECT SUM(oi.qty) 
        FROM order_items oi
        JOIN orders o ON o.id = oi.order_id
        WHERE DATE(o.created_at) = ? AND o.deleted_at IS NULL
    """, (today,))
    ingressos_hoje = cur.fetchone()[0] or 0
    
    # Receita hoje (nova arquitetura)
    cur.execute("""
        SELECT SUM(oi.qty * oi.unit_price_cents) 
        FROM order_items oi
        JOIN orders o ON o.id = oi.order_id
        WHERE DATE(o.created_at) = ? AND o.deleted_at IS NULL
    """, (today,))
    receita_hoje = (cur.fetchone()[0] or 0) / 100
    
    # Inteiras hoje (nova arquitetura)
    cur.execute("""
        SELECT SUM(oi.qty) 
        FROM order_items oi
        JOIN orders o ON o.id = oi.order_id
        WHERE DATE(o.created_at) = ? AND oi.ticket_type = 'inteira' AND o.deleted_at IS NULL
    """, (today,))
    inteiras_hoje = cur.fetchone()[0] or 0
    
    # Meias hoje (nova arquitetura)
    cur.execute("""
        SELECT SUM(oi.qty) 
        FROM order_items oi
        JOIN orders o ON o.id = oi.order_id
        WHERE DATE(o.created_at) = ? AND oi.ticket_type = 'meia' AND o.deleted_at IS NULL
    """, (today,))
    meias_hoje = cur.fetchone()[0] or 0
    
    # Gratuitas hoje (nova arquitetura)
    cur.execute("""
        SELECT SUM(oi.qty) 
        FROM order_items oi
        JOIN orders o ON o.id = oi.order_id
        WHERE DATE(o.created_at) = ? AND oi.ticket_type = 'gratuita' AND o.deleted_at IS NULL
    """, (today,))
    gratuitas_hoje = cur.fetchone()[0] or 0
    
    # Dados de pagamento hoje
    cur.execute("""
        SELECT o.payment_method, SUM(oi.qty * oi.unit_price_cents) as receita
        FROM order_items oi
        JOIN orders o ON o.id = oi.order_id
        WHERE DATE(o.created_at) = ? AND o.deleted_at IS NULL
        GROUP BY o.payment_method
    """, (today,))
    pagamentos_hoje = cur.fetchall()
    
    # Calcula receita por forma de pagamento
    credito_hoje = 0
    debito_hoje = 0
    pix_hoje = 0
    
    for metodo, receita in pagamentos_hoje:
        receita_valor = (receita or 0) / 100
        if metodo == 'credito':
            credito_hoje = receita_valor
        elif metodo == 'debito':
            debito_hoje = receita_valor
        elif metodo == 'pix':
            pix_hoje = receita_valor
    
    # Pedidos recentes do dia (últimas 10) - nova arquitetura
    cur.execute("""
        SELECT o.id, o.created_at, o.channel, o.state, o.city, o.note,
               GROUP_CONCAT(oi.ticket_type || ':' || oi.qty, ', ') as items
        FROM orders o
        LEFT JOIN order_items oi ON oi.order_id = o.id
        WHERE DATE(o.created_at) = ? AND o.deleted_at IS NULL
        GROUP BY o.id
        ORDER BY o.created_at DESC 
        LIMIT 10
    """, (today,))
    pedidos_recentes = cur.fetchall()
    
    con.close()
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request, 
        "user": get_user_info(request),
        "ingressos_hoje": ingressos_hoje,
        "receita_hoje": f"{receita_hoje:.2f}",
        "inteiras_hoje": inteiras_hoje,
        "meias_hoje": meias_hoje,
        "gratuitas_hoje": gratuitas_hoje,
        "credito_hoje": f"{credito_hoje:.2f}",
        "debito_hoje": f"{debito_hoje:.2f}",
        "pix_hoje": f"{pix_hoje:.2f}",
        "pedidos_recentes": pedidos_recentes
    })

@app.get("/sell", response_class=HTMLResponse)
def sell_page(request: Request):
    """Página de vendas individuais"""
    if not current_user(request):
        return RedirectResponse("/login")
    
    return templates.TemplateResponse("sell.html", {
        "request": request,
        "user": get_user_info(request)
    })

@app.get("/groups", response_class=HTMLResponse)
def groups_page(request: Request):
    """Página de vendas em grupo"""
    if not current_user(request):
        return RedirectResponse("/login")
    
    return templates.TemplateResponse("groups.html", {
        "request": request,
        "user": get_user_info(request)
    })

@app.post("/groups/new")
def create_group(
    request: Request,
    visit_type: str = Form(...),
    has_oficio: int = Form(...),
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
    payment_method: str = Form(...)
):
    """Registra venda em grupo usando nova arquitetura"""
    if not current_user(request):
        return RedirectResponse("/login", status_code=303)
    
    user = current_user(request)
    
    # Define os itens com quantidades, preços e motivos
    items = [
        ("inteira", qtd_inteira, 1000, None),
        ("meia", qtd_meia, 500, reason_meia),
        ("gratuita", qtd_gratuita, 0, reason_gratuita),
    ]
    
    # Verifica se pelo menos um item foi selecionado
    if sum(q for _, q, _, _ in items) <= 0:
        return RedirectResponse("/groups", status_code=303)
    
    try:
        con = sqlite3.connect(DB)
        cur = con.cursor()
        
        # Cria o pedido (order) para grupo
        now = datetime.now().isoformat()
        cur.execute("""
            INSERT INTO orders(created_at, operator_username, channel, state, city, note, payment_method)
            VALUES(?, ?, 'grupo', ?, ?, ?, ?)
        """, (now, user, state, city, note, payment_method))
        
        order_id = cur.lastrowid
        
        # Insere os itens do pedido
        for tipo, qtd, preco, motivo in items:
            if qtd and qtd > 0:
                cur.execute("""
                    INSERT INTO order_items(order_id, ticket_type, qty, unit_price_cents, reason)
                    VALUES(?, ?, ?, ?, ?)
                """, (order_id, tipo, qtd, preco, motivo))
        
        # Insere os dados do grupo
        cur.execute("""
            INSERT INTO groups(order_id, visit_type, has_oficio, institution_name, 
                             total_students, total_teachers, responsible_name, 
                             state, city, ies_municipio, scheduled_date)
            VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (order_id, visit_type, has_oficio, institution_name, total_students, 
              total_teachers, responsible_name, state, city, ies_municipio, scheduled_date))
        
        con.commit()
        con.close()
        
        return RedirectResponse("/dashboard", status_code=303)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao salvar grupo: {str(e)}")

@app.post("/sell")
def sell_post(
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
    payment_method: str = Form(...)
):
    """Registra venda com tipos mistos usando nova arquitetura"""
    if not current_user(request):
        return RedirectResponse("/login", status_code=303)
    
    user = current_user(request)
    
    # Define os itens com quantidades, preços e motivos
    items = [
        ("inteira", qtd_inteira, 1000, None),
        ("meia", qtd_meia, 500, reason_meia),
        ("gratuita", qtd_gratuita, 0, reason_gratuita),
    ]
    
    # Verifica se pelo menos um item foi selecionado
    if sum(q for _, q, _, _ in items) <= 0:
        return RedirectResponse("/sell", status_code=303)
    
    try:
        con = sqlite3.connect(DB)
        cur = con.cursor()
        
        # Cria o pedido (order)
        now = datetime.now().isoformat()
        cur.execute("""
            INSERT INTO orders(created_at, operator_username, channel, state, city, note, payment_method)
            VALUES(?, ?, 'balcao', ?, ?, ?, ?)
        """, (now, user, state, city, note, payment_method))
        
        order_id = cur.lastrowid
        
        # Insere os itens do pedido
        for tipo, qtd, preco, motivo in items:
            if qtd and qtd > 0:
                cur.execute("""
                    INSERT INTO order_items(order_id, ticket_type, qty, unit_price_cents, reason)
                    VALUES(?, ?, ?, ?, ?)
                """, (order_id, tipo, qtd, preco, motivo))
        
        con.commit()
        con.close()
        
        return RedirectResponse("/dashboard", status_code=303)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao salvar venda: {str(e)}")

@app.post("/orders/{order_id}/delete")
def delete_order(request: Request, order_id: int):
    """Soft delete de um pedido (apenas admin e gestora)"""
    if not current_user(request):
        return RedirectResponse("/login", status_code=303)
    
    if not require_role(request, {"admin", "gestora"}):
        return RedirectResponse("/unauthorized", status_code=303)
    
    try:
        con = sqlite3.connect(DB)
        cur = con.cursor()
        
        # Verifica se o pedido existe e é do dia atual
        today = datetime.now().strftime('%Y-%m-%d')
        cur.execute("""
            SELECT id, created_at FROM orders 
            WHERE id = ? AND DATE(created_at) = ? AND deleted_at IS NULL
        """, (order_id, today))
        
        order = cur.fetchone()
        if not order:
            con.close()
            raise HTTPException(status_code=404, detail="Pedido não encontrado ou não pode ser excluído")
        
        # Soft delete - marca como deletado
        now = datetime.now().isoformat()
        cur.execute("UPDATE orders SET deleted_at = ? WHERE id = ?", (now, order_id))
        con.commit()
        con.close()
        
        return RedirectResponse("/dashboard", status_code=303)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao excluir pedido: {str(e)}")

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

@app.get("/reports/reasons", response_class=HTMLResponse)
def reports_reasons_page(request: Request, start_date: Optional[str] = None, end_date: Optional[str] = None, state: Optional[str] = None):
    """Página de relatórios por motivos"""
    if not current_user(request):
        return RedirectResponse("/login")
    
    user = current_user(request)
    
    # Busca dados de meias por motivo
    con = sqlite3.connect(DB)
    cur = con.cursor()
    
    # Query para meias por motivo
    meias_query = """
        SELECT oi.reason, SUM(oi.qty) as qtd, ROUND(SUM(oi.qty * oi.unit_price_cents)/100.0, 2) as receita
        FROM order_items oi
        JOIN orders o ON o.id = oi.order_id
        WHERE oi.ticket_type = 'meia' AND o.deleted_at IS NULL
    """
    params = []
    
    if start_date:
        meias_query += " AND DATE(o.created_at) >= ?"
        params.append(start_date)
    if end_date:
        meias_query += " AND DATE(o.created_at) <= ?"
        params.append(end_date)
    if state:
        meias_query += " AND o.state = ?"
        params.append(state)
    
    meias_query += " GROUP BY oi.reason ORDER BY qtd DESC"
    
    cur.execute(meias_query, params)
    meias_reasons = cur.fetchall()
    
    # Query para gratuitas por motivo
    gratuitas_query = """
        SELECT oi.reason, SUM(oi.qty) as qtd
        FROM order_items oi
        JOIN orders o ON o.id = oi.order_id
        WHERE oi.ticket_type = 'gratuita' AND o.deleted_at IS NULL
    """
    params_gratuitas = []
    
    if start_date:
        gratuitas_query += " AND DATE(o.created_at) >= ?"
        params_gratuitas.append(start_date)
    if end_date:
        gratuitas_query += " AND DATE(o.created_at) <= ?"
        params_gratuitas.append(end_date)
    if state:
        gratuitas_query += " AND o.state = ?"
        params_gratuitas.append(state)
    
    gratuitas_query += " GROUP BY oi.reason ORDER BY qtd DESC"
    
    cur.execute(gratuitas_query, params_gratuitas)
    gratuitas_reasons = cur.fetchall()
    
    con.close()
    
    return templates.TemplateResponse("reports_reasons.html", {
        "request": request,
        "user": {"username": user},
        "start_date": start_date,
        "end_date": end_date,
        "state": state,
        "meias_reasons": meias_reasons,
        "gratuitas_reasons": gratuitas_reasons
    })

@app.get("/reports/groups", response_class=HTMLResponse)
def reports_groups_page(request: Request, start_date: Optional[str] = None, end_date: Optional[str] = None, visit_type: Optional[str] = None):
    """Página de relatórios de grupos"""
    if not current_user(request):
        return RedirectResponse("/login")
    
    user = current_user(request)
    
    # Busca dados de grupos
    con = sqlite3.connect(DB)
    cur = con.cursor()
    
    groups_query = """
        SELECT DATE(o.created_at) as data, g.visit_type, g.has_oficio, g.institution_name, 
               g.responsible_name, g.state, g.city, g.total_students, g.total_teachers,
               ROUND(SUM(oi.qty * oi.unit_price_cents)/100.0, 2) as receita
        FROM groups g
        JOIN orders o ON o.id = g.order_id
        LEFT JOIN order_items oi ON oi.order_id = o.id
        WHERE o.deleted_at IS NULL
    """
    params = []
    
    if start_date:
        groups_query += " AND DATE(o.created_at) >= ?"
        params.append(start_date)
    if end_date:
        groups_query += " AND DATE(o.created_at) <= ?"
        params.append(end_date)
    if visit_type:
        groups_query += " AND g.visit_type = ?"
        params.append(visit_type)
    
    groups_query += " GROUP BY g.id ORDER BY o.created_at DESC"
    
    cur.execute(groups_query, params)
    groups_data = cur.fetchall()
    
    con.close()
    
    return templates.TemplateResponse("reports_groups.html", {
        "request": request,
        "user": {"username": user},
        "start_date": start_date,
        "end_date": end_date,
        "visit_type": visit_type,
        "groups_data": groups_data
    })

@app.get("/api/reports/summary")
def get_reports_summary(request: Request):
    """Retorna resumo das vendas usando nova arquitetura"""
    if not current_user(request):
        raise HTTPException(status_code=401, detail="Não autenticado")
    
    try:
        con = sqlite3.connect(DB)
        df = pd.read_sql_query("""
            SELECT DATE(o.created_at) AS dia,
                   SUM(oi.qty) AS ingressos,
                   ROUND(SUM(oi.qty*oi.unit_price_cents)/100.0, 2) AS total_reais
            FROM order_items oi
            JOIN orders o ON o.id = oi.order_id
            WHERE o.deleted_at IS NULL
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
    """Exporta relatório geral para Excel com múltiplas abas"""
    if not current_user(request):
        raise HTTPException(status_code=401, detail="Não autenticado")
    
    try:
        con = sqlite3.connect(DB)
        
        # Aba 1: Visão Geral por Dia e Tipo
        overview = pd.read_sql_query("""
            SELECT DATE(o.created_at) AS dia,
                   oi.ticket_type AS tipo,
                   SUM(oi.qty) AS quantidade,
                   ROUND(SUM(oi.qty*oi.unit_price_cents)/100.0, 2) AS total_reais
            FROM order_items oi
            JOIN orders o ON o.id = oi.order_id
            WHERE o.deleted_at IS NULL
            GROUP BY dia, ticket_type
            ORDER BY dia DESC, ticket_type;
        """, con)
        
        # Aba 2: Por UF
        by_uf = pd.read_sql_query("""
            SELECT COALESCE(o.state, 'Não informado') AS uf,
                   SUM(oi.qty) AS ingressos,
                   ROUND(SUM(oi.qty*oi.unit_price_cents)/100.0, 2) AS receita
            FROM order_items oi
            JOIN orders o ON o.id = oi.order_id
            WHERE o.deleted_at IS NULL
            GROUP BY o.state
            ORDER BY receita DESC;
        """, con)
        
        # Aba 3: Por Tipo de Ingresso
        by_type = pd.read_sql_query("""
            SELECT oi.ticket_type AS tipo,
                   SUM(oi.qty) AS ingressos,
                   ROUND(SUM(oi.qty*oi.unit_price_cents)/100.0, 2) AS receita
            FROM order_items oi
            JOIN orders o ON o.id = oi.order_id
            WHERE o.deleted_at IS NULL
            GROUP BY oi.ticket_type
            ORDER BY receita DESC;
        """, con)
        
        # Aba 4: Por Dia
        by_day = pd.read_sql_query("""
            SELECT DATE(o.created_at) AS dia,
                   SUM(oi.qty) AS ingressos,
                   ROUND(SUM(oi.qty*oi.unit_price_cents)/100.0, 2) AS receita
            FROM order_items oi
            JOIN orders o ON o.id = oi.order_id
            WHERE o.deleted_at IS NULL
            GROUP BY DATE(o.created_at)
            ORDER BY dia DESC;
        """, con)
        
        # Aba 5: Por Forma de Pagamento (NOVA)
        by_payment = pd.read_sql_query("""
            SELECT COALESCE(o.payment_method, 'Não informado') AS forma_pagamento,
                   SUM(oi.qty) AS ingressos,
                   ROUND(SUM(oi.qty*oi.unit_price_cents)/100.0, 2) AS receita
            FROM order_items oi
            JOIN orders o ON o.id = oi.order_id
            WHERE o.deleted_at IS NULL
            GROUP BY o.payment_method
            ORDER BY receita DESC;
        """, con)
        
        con.close()
        
        if overview.empty:
            raise HTTPException(status_code=404, detail="Não há vendas para exportar")
        
        # Salva arquivo temporário
        filename = f"relatorio_vendas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        filepath = f"temp/{filename}"
        
        # Cria diretório temp se não existir
        os.makedirs("temp", exist_ok=True)
        
        # Cria Excel com múltiplas abas
        with pd.ExcelWriter(filepath, engine='xlsxwriter') as writer:
            overview.to_excel(writer, sheet_name='Visao_Geral', index=False)
            by_uf.to_excel(writer, sheet_name='Por_UF', index=False)
            by_type.to_excel(writer, sheet_name='Por_Tipo', index=False)
            by_day.to_excel(writer, sheet_name='Por_Dia', index=False)
            by_payment.to_excel(writer, sheet_name='Por_Pagamento', index=False)
        
        return FileResponse(
            path=filepath,
            filename=filename,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao exportar: {str(e)}")

@app.get("/api/reports/reasons/export")
def export_reasons_reports(request: Request, type: str, start: Optional[str] = None, end: Optional[str] = None, state: Optional[str] = None):
    """Exporta relatório de motivos para Excel"""
    if not current_user(request):
        raise HTTPException(status_code=401, detail="Não autenticado")
    
    try:
        con = sqlite3.connect(DB)
        
        if type == "meia":
            query = """
                SELECT oi.reason AS motivo, SUM(oi.qty) AS quantidade, 
                       ROUND(SUM(oi.qty * oi.unit_price_cents)/100.0, 2) AS receita
                FROM order_items oi
                JOIN orders o ON o.id = oi.order_id
                WHERE oi.ticket_type = 'meia' AND o.deleted_at IS NULL
            """
        else:  # gratuita
            query = """
                SELECT oi.reason AS motivo, SUM(oi.qty) AS quantidade, 0 AS receita
                FROM order_items oi
                JOIN orders o ON o.id = oi.order_id
                WHERE oi.ticket_type = 'gratuita' AND o.deleted_at IS NULL
            """
        
        params = []
        if start:
            query += " AND DATE(o.created_at) >= ?"
            params.append(start)
        if end:
            query += " AND DATE(o.created_at) <= ?"
            params.append(end)
        if state:
            query += " AND o.state = ?"
            params.append(state)
        
        query += " GROUP BY oi.reason ORDER BY quantidade DESC"
        
        df = pd.read_sql_query(query, con, params=params)
        con.close()
        
        if df.empty:
            raise HTTPException(status_code=404, detail="Não há dados para exportar")
        
        # Salva arquivo temporário
        filename = f"relatorio_motivos_{type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
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

@app.get("/api/reports/groups/export")
def export_groups_reports(request: Request, start: Optional[str] = None, end: Optional[str] = None, visit_type: Optional[str] = None):
    """Exporta relatório de grupos para Excel"""
    if not current_user(request):
        raise HTTPException(status_code=401, detail="Não autenticado")
    
    try:
        con = sqlite3.connect(DB)
        
        query = """
            SELECT DATE(o.created_at) as data, g.visit_type as tipo_visita, 
                   CASE WHEN g.has_oficio = 1 THEN 'Sim' ELSE 'Não' END as oficio,
                   g.institution_name as instituicao, g.responsible_name as responsavel,
                   g.state as uf, g.city as cidade, g.total_students as estudantes,
                   g.total_teachers as professores,
                   ROUND(SUM(oi.qty * oi.unit_price_cents)/100.0, 2) as receita
            FROM groups g
            JOIN orders o ON o.id = g.order_id
            LEFT JOIN order_items oi ON oi.order_id = o.id
            WHERE o.deleted_at IS NULL
        """
        
        params = []
        if start:
            query += " AND DATE(o.created_at) >= ?"
            params.append(start)
        if end:
            query += " AND DATE(o.created_at) <= ?"
            params.append(end)
        if visit_type:
            query += " AND g.visit_type = ?"
            params.append(visit_type)
        
        query += " GROUP BY g.id ORDER BY o.created_at DESC"
        
        df = pd.read_sql_query(query, con, params=params)
        con.close()
        
        if df.empty:
            raise HTTPException(status_code=404, detail="Não há grupos para exportar")
        
        # Salva arquivo temporário
        filename = f"relatorio_grupos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
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

# ===== ROTAS DE ADMIN =====

@app.get("/admin", response_class=HTMLResponse)
def admin_home(request: Request):
    """Página inicial do admin (apenas admin e gestora)"""
    if not current_user(request):
        return RedirectResponse("/login")
    
    if not require_role(request, {"admin", "gestora"}):
        return RedirectResponse("/unauthorized", status_code=303)
    
    user = current_user(request)
    return templates.TemplateResponse("admin_home.html", {
        "request": request,
        "user": {"username": user}
    })

@app.get("/admin/orders", response_class=HTMLResponse)
def admin_orders(request: Request, start_date: Optional[str] = None, end_date: Optional[str] = None, 
                 state: Optional[str] = None, q: Optional[str] = None, page: int = 1):
    """Lista de pedidos para administração (apenas admin e gestora)"""
    if not current_user(request):
        return RedirectResponse("/login")
    
    if not require_role(request, {"admin", "gestora"}):
        return RedirectResponse("/unauthorized", status_code=303)
    
    user = current_user(request)
    
    # Paginação
    limit = 20
    offset = (page - 1) * limit
    
    # Query principal
    query = """
        SELECT o.id, o.created_at, o.operator_username, o.state, o.city, o.note,
               SUM(CASE WHEN oi.ticket_type='inteira' THEN oi.qty ELSE 0 END) AS inteiras,
               SUM(CASE WHEN oi.ticket_type='meia' THEN oi.qty ELSE 0 END) AS meias,
               SUM(CASE WHEN oi.ticket_type='gratuita' THEN oi.qty ELSE 0 END) AS gratuitas,
               ROUND(SUM(oi.qty * oi.unit_price_cents)/100.0, 2) AS receita
        FROM orders o
        LEFT JOIN order_items oi ON oi.order_id = o.id
        WHERE o.deleted_at IS NULL
    """
    
    params = []
    if start_date:
        query += " AND DATE(o.created_at) >= ?"
        params.append(start_date)
    if end_date:
        query += " AND DATE(o.created_at) <= ?"
        params.append(end_date)
    if state:
        query += " AND o.state = ?"
        params.append(state)
    if q:
        query += " AND (o.city LIKE ? OR o.operator_username LIKE ? OR o.note LIKE ?)"
        search_term = f"%{q}%"
        params.extend([search_term, search_term, search_term])
    
    query += " GROUP BY o.id ORDER BY o.created_at DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    
    con = sqlite3.connect(DB)
    cur = con.cursor()
    cur.execute(query, params)
    orders = cur.fetchall()
    
    # Contar total para paginação
    count_query = """
        SELECT COUNT(DISTINCT o.id)
        FROM orders o
        WHERE o.deleted_at IS NULL
    """
    count_params = []
    if start_date:
        count_query += " AND DATE(o.created_at) >= ?"
        count_params.append(start_date)
    if end_date:
        count_query += " AND DATE(o.created_at) <= ?"
        count_params.append(end_date)
    if state:
        count_query += " AND o.state = ?"
        count_params.append(state)
    if q:
        count_query += " AND (o.city LIKE ? OR o.operator_username LIKE ? OR o.note LIKE ?)"
        search_term = f"%{q}%"
        count_params.extend([search_term, search_term, search_term])
    
    cur.execute(count_query, count_params)
    total_orders = cur.fetchone()[0]
    total_pages = (total_orders + limit - 1) // limit
    
    con.close()
    
    return templates.TemplateResponse("admin_orders.html", {
        "request": request,
        "user": {"username": user},
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

@app.get("/admin/groups", response_class=HTMLResponse)
def admin_groups(request: Request, start_date: Optional[str] = None, end_date: Optional[str] = None, 
                 state: Optional[str] = None, q: Optional[str] = None, page: int = 1):
    """Lista de grupos para administração (apenas admin e gestora)"""
    if not current_user(request):
        return RedirectResponse("/login")
    
    if not require_role(request, {"admin", "gestora"}):
        return RedirectResponse("/unauthorized", status_code=303)
    
    user = current_user(request)
    
    # Paginação
    limit = 20
    offset = (page - 1) * limit
    
    # Query principal
    query = """
        SELECT g.id, o.created_at, g.visit_type, g.has_oficio, g.institution_name, 
               g.responsible_name, g.state, g.city, g.total_students, g.total_teachers,
               ROUND(SUM(oi.qty * oi.unit_price_cents)/100.0, 2) AS receita
        FROM groups g
        JOIN orders o ON o.id = g.order_id
        LEFT JOIN order_items oi ON oi.order_id = o.id
        WHERE o.deleted_at IS NULL
    """
    
    params = []
    if start_date:
        query += " AND DATE(o.created_at) >= ?"
        params.append(start_date)
    if end_date:
        query += " AND DATE(o.created_at) <= ?"
        params.append(end_date)
    if state:
        query += " AND g.state = ?"
        params.append(state)
    if q:
        query += " AND (g.institution_name LIKE ? OR g.responsible_name LIKE ? OR g.city LIKE ?)"
        search_term = f"%{q}%"
        params.extend([search_term, search_term, search_term])
    
    query += " GROUP BY g.id ORDER BY o.created_at DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    
    con = sqlite3.connect(DB)
    cur = con.cursor()
    cur.execute(query, params)
    groups = cur.fetchall()
    
    # Contar total para paginação
    count_query = """
        SELECT COUNT(DISTINCT g.id)
        FROM groups g
        JOIN orders o ON o.id = g.order_id
        WHERE o.deleted_at IS NULL
    """
    count_params = []
    if start_date:
        count_query += " AND DATE(o.created_at) >= ?"
        count_params.append(start_date)
    if end_date:
        count_query += " AND DATE(o.created_at) <= ?"
        count_params.append(end_date)
    if state:
        count_query += " AND g.state = ?"
        count_params.append(state)
    if q:
        count_query += " AND (g.institution_name LIKE ? OR g.responsible_name LIKE ? OR g.city LIKE ?)"
        search_term = f"%{q}%"
        count_params.extend([search_term, search_term, search_term])
    
    cur.execute(count_query, count_params)
    total_groups = cur.fetchone()[0]
    total_pages = (total_groups + limit - 1) // limit
    
    con.close()
    
    return templates.TemplateResponse("admin_groups.html", {
        "request": request,
        "user": {"username": user},
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

@app.get("/admin/orders/{order_id}/edit", response_class=HTMLResponse)
def admin_order_edit(request: Request, order_id: int):
    """Formulário de edição de pedido (apenas admin e gestora)"""
    if not current_user(request):
        return RedirectResponse("/login")
    
    if not require_role(request, {"admin", "gestora"}):
        return RedirectResponse("/unauthorized", status_code=303)
    
    user = current_user(request)
    
    con = sqlite3.connect(DB)
    cur = con.cursor()
    
    # Busca dados do pedido
    cur.execute("""
        SELECT id, created_at, operator_username, state, city, note
        FROM orders 
        WHERE id = ? AND deleted_at IS NULL
    """, (order_id,))
    
    order = cur.fetchone()
    if not order:
        con.close()
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    
    # Busca itens do pedido
    cur.execute("""
        SELECT ticket_type, qty, reason
        FROM order_items 
        WHERE order_id = ?
        ORDER BY ticket_type
    """, (order_id,))
    
    items = cur.fetchall()
    con.close()
    
    # Organiza os dados
    order_data = {
        "id": order[0],
        "created_at": order[1],
        "operator_username": order[2],
        "state": order[3],
        "city": order[4],
        "note": order[5],
        "qtd_inteira": 0,
        "qtd_meia": 0,
        "qtd_gratuita": 0,
        "reason_meia": None,
        "reason_gratuita": None
    }
    
    for item in items:
        if item[0] == "inteira":
            order_data["qtd_inteira"] = item[1]
        elif item[0] == "meia":
            order_data["qtd_meia"] = item[1]
            order_data["reason_meia"] = item[2]
        elif item[0] == "gratuita":
            order_data["qtd_gratuita"] = item[1]
            order_data["reason_gratuita"] = item[2]
    
    return templates.TemplateResponse("admin_order_edit.html", {
        "request": request,
        "user": {"username": user},
        "order": order_data
    })

@app.post("/admin/orders/{order_id}/edit")
def admin_order_update(request: Request, order_id: int,
                      qtd_inteira: int = Form(0),
                      qtd_meia: int = Form(0),
                      qtd_gratuita: int = Form(0),
                      reason_meia: Optional[str] = Form(None),
                      reason_gratuita: Optional[str] = Form(None),
                      name: Optional[str] = Form(None),
                      state: Optional[str] = Form(None),
                      city: Optional[str] = Form(None),
                      note: Optional[str] = Form(None)):
    """Salva edição de pedido"""
    if not current_user(request):
        return RedirectResponse("/login", status_code=303)
    
    user = current_user(request)
    
    try:
        con = sqlite3.connect(DB)
        cur = con.cursor()
        
        # Verifica se o pedido existe
        cur.execute("SELECT id FROM orders WHERE id = ? AND deleted_at IS NULL", (order_id,))
        if not cur.fetchone():
            con.close()
            raise HTTPException(status_code=404, detail="Pedido não encontrado")
        
        # Atualiza dados do pedido
        cur.execute("""
            UPDATE orders 
            SET state = ?, city = ?, note = ?
            WHERE id = ?
        """, (state, city, note, order_id))
        
        # Remove itens antigos
        cur.execute("DELETE FROM order_items WHERE order_id = ?", (order_id,))
        
        # Insere novos itens
        items = [
            ("inteira", qtd_inteira, 1000, None),
            ("meia", qtd_meia, 500, reason_meia),
            ("gratuita", qtd_gratuita, 0, reason_gratuita),
        ]
        
        for tipo, qtd, preco, motivo in items:
            if qtd and qtd > 0:
                cur.execute("""
                    INSERT INTO order_items(order_id, ticket_type, qty, unit_price_cents, reason)
                    VALUES(?, ?, ?, ?, ?)
                """, (order_id, tipo, qtd, preco, motivo))
        
        # Log da edição
        now = datetime.now().isoformat()
        cur.execute("""
            INSERT INTO order_events(order_id, action, who, when_created, reason)
            VALUES(?, 'edit', ?, ?, ?)
        """, (order_id, user, now, "Edição via admin"))
        
        con.commit()
        con.close()
        
        return RedirectResponse("/admin/orders", status_code=303)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao salvar edição: {str(e)}")

@app.post("/admin/orders/{order_id}/delete")
def admin_order_delete(request: Request, order_id: int, reason: str = Form("")):
    """Exclusão soft de pedido (apenas admin e gestora)"""
    if not current_user(request):
        return RedirectResponse("/login", status_code=303)
    
    if not require_role(request, {"admin", "gestora"}):
        return RedirectResponse("/unauthorized", status_code=303)
    
    user = current_user(request)
    
    try:
        con = sqlite3.connect(DB)
        cur = con.cursor()
        
        # Verifica se o pedido existe
        cur.execute("SELECT id, created_at FROM orders WHERE id = ? AND deleted_at IS NULL", (order_id,))
        order = cur.fetchone()
        if not order:
            con.close()
            raise HTTPException(status_code=404, detail="Pedido não encontrado")
        
        # Soft delete
        now = datetime.now().isoformat()
        cur.execute("UPDATE orders SET deleted_at = ? WHERE id = ?", (now, order_id))
        
        # Log da exclusão
        cur.execute("""
            INSERT INTO order_events(order_id, action, who, when_created, reason)
            VALUES(?, 'delete', ?, ?, ?)
        """, (order_id, user, now, reason or "Exclusão via admin"))
        
        con.commit()
        con.close()
        
        return RedirectResponse("/admin/orders", status_code=303)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao excluir pedido: {str(e)}")

@app.post("/admin/groups/{group_id}/delete")
def admin_group_delete(request: Request, group_id: int, reason: str = Form("")):
    """Exclusão soft de grupo (apenas admin e gestora)"""
    if not current_user(request):
        return RedirectResponse("/login", status_code=303)
    
    if not require_role(request, {"admin", "gestora"}):
        return RedirectResponse("/unauthorized", status_code=303)
    
    user = current_user(request)
    
    try:
        con = sqlite3.connect(DB)
        cur = con.cursor()
        
        # Busca o order_id do grupo
        cur.execute("SELECT order_id FROM groups WHERE id = ?", (group_id,))
        group = cur.fetchone()
        if not group:
            con.close()
            raise HTTPException(status_code=404, detail="Grupo não encontrado")
        
        order_id = group[0]
        
        # Verifica se o pedido existe
        cur.execute("SELECT id FROM orders WHERE id = ? AND deleted_at IS NULL", (order_id,))
        if not cur.fetchone():
            con.close()
            raise HTTPException(status_code=404, detail="Pedido não encontrado")
        
        # Soft delete
        now = datetime.now().isoformat()
        cur.execute("UPDATE orders SET deleted_at = ? WHERE id = ?", (now, order_id))
        
        # Log da exclusão
        cur.execute("""
            INSERT INTO order_events(order_id, action, who, when_created, reason)
            VALUES(?, 'delete', ?, ?, ?)
        """, (order_id, user, now, reason or "Exclusão de grupo via admin"))
        
        con.commit()
        con.close()
        
        return RedirectResponse("/admin/groups", status_code=303)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao excluir grupo: {str(e)}")

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
