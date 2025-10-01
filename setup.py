# setup.py
# Script de configuração inicial do sistema

import os
import sys
import subprocess
import sqlite3
import bcrypt
from config import get_config

def check_python_version():
    """Verifica se a versão do Python é compatível"""
    print("Verificando versao do Python...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("ERRO: Python 3.8+ e necessario. Versao atual:", f"{version.major}.{version.minor}")
        return False
    print(f"OK: Python {version.major}.{version.minor}.{version.micro}")
    return True

def install_dependencies():
    """Instala as dependências necessárias"""
    print("\n📦 Instalando dependências...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True, capture_output=True)
        print("✅ Dependências instaladas com sucesso!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao instalar dependências: {e}")
        return False

def create_directories():
    """Cria diretórios necessários"""
    print("\n📁 Criando diretórios...")
    dirs = ["templates", "static", "temp", "dist"]
    for dir_name in dirs:
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
            print(f"✅ Diretório {dir_name} criado")
        else:
            print(f"✅ Diretório {dir_name} já existe")

def init_database():
    """Inicializa o banco de dados"""
    print("\n🗄️ Inicializando banco de dados...")
    try:
        config = get_config()
        con = sqlite3.connect(config["database_url"])
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
        cur.execute("SELECT 1 FROM users WHERE username=?", (config["default_user"]["username"],))
        if not cur.fetchone():
            password = config["default_user"]["password"].encode()
            cur.execute("INSERT INTO users(username,password_hash,role) VALUES (?,?,?)",
                        (config["default_user"]["username"], 
                         bcrypt.hashpw(password, bcrypt.gensalt()), 
                         config["default_user"]["role"]))
            print(f"✅ Usuário padrão criado: {config['default_user']['username']}")
        
        con.commit()
        con.close()
        print("✅ Banco de dados inicializado com sucesso!")
        return True
    except Exception as e:
        print(f"❌ Erro ao inicializar banco: {e}")
        return False

def test_imports():
    """Testa se todas as dependências podem ser importadas"""
    print("\n🧪 Testando importações...")
    modules = [
        "fastapi", 
        "uvicorn",
        "pandas",
        "openpyxl",
        "bcrypt",
        "jinja2",
        "webview"
    ]
    
    for module in modules:
        try:
            __import__(module)
            print(f"✅ {module} - OK")
        except ImportError as e:
            print(f"❌ {module} - ERRO: {e}")
            return False
    return True

def create_sample_data():
    """Cria dados de exemplo para teste"""
    print("\n📊 Criando dados de exemplo...")
    try:
        config = get_config()
        con = sqlite3.connect(config["database_url"])
        cur = con.cursor()
        
        # Verifica se já existem vendas
        cur.execute("SELECT COUNT(*) FROM sales")
        count = cur.fetchone()[0]
        
        if count == 0:
            from datetime import datetime, timedelta
            import random
            
            # Cria vendas de exemplo dos últimos 7 dias
            for i in range(7):
                date = datetime.now() - timedelta(days=i)
                for j in range(random.randint(5, 15)):  # 5-15 vendas por dia
                    ticket_type = random.choice(config["ticket_types"])
                    qty = random.randint(1, 4)
                    price = config["prices"][ticket_type]
                    
                    cur.execute("""INSERT INTO sales(sold_at,ticket_type,qty,unit_price_cents,operator_username,name,state,city,note)
                                   VALUES(?,?,?,?,?,?,?,?,?)""",
                                (date.isoformat(), ticket_type, qty, price, config["default_user"]["username"],
                                 f"Cliente {j+1}", "PE", "Recife", f"Venda de exemplo {j+1}"))
            
            con.commit()
            print("✅ Dados de exemplo criados!")
        else:
            print("✅ Dados já existem, pulando criação de exemplo")
        
        con.close()
        return True
    except Exception as e:
        print(f"❌ Erro ao criar dados de exemplo: {e}")
        return False

def main():
    """Função principal de setup"""
    print("Configurando Sistema de Bilheteria - Museu Cais do Sertao")
    print("=" * 60)
    
    # Verificações
    if not check_python_version():
        sys.exit(1)
    
    if not install_dependencies():
        sys.exit(1)
    
    if not test_imports():
        print("\n❌ Algumas dependências falharam. Tente reinstalar:")
        print("pip install -r requirements.txt --force-reinstall")
        sys.exit(1)
    
    # Configuração
    create_directories()
    
    if not init_database():
        sys.exit(1)
    
    create_sample_data()
    
    print("\n" + "=" * 60)
    print("🎉 Configuração concluída com sucesso!")
    print("\n📋 Próximos passos:")
    print("1. Teste a aplicação web: python run_web.py")
    print("2. Acesse: http://127.0.0.1:8000")
    print("3. Para criar executável: python build.py")
    print("\n🔑 Credenciais de login:")
    config = get_config()
    print(f"   Usuário: {config['default_user']['username']}")
    print(f"   Senha: {config['default_user']['password']}")
    print("\n📚 Documentação:")
    print("   README.md - Visão geral")
    print("   INSTALACAO.md - Guia de instalação")
    print("   USO.md - Manual de uso")
    print("\n🚀 Sistema pronto para uso!")

if __name__ == "__main__":
    main()
