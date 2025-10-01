# setup_simple.py
# Script de configuração inicial do sistema (versão simples)

import os
import sys
import subprocess
import sqlite3
import bcrypt

def install_dependencies():
    """Instala as dependências necessárias"""
    print("Instalando dependencias...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True, capture_output=True)
        print("Dependencias instaladas com sucesso!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Erro ao instalar dependencias: {e}")
        return False

def create_directories():
    """Cria diretórios necessários"""
    print("Criando diretorios...")
    dirs = ["templates", "static", "temp", "dist"]
    for dir_name in dirs:
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
            print(f"Diretorio {dir_name} criado")
        else:
            print(f"Diretorio {dir_name} ja existe")

def init_database():
    """Inicializa o banco de dados"""
    print("Inicializando banco de dados...")
    try:
        con = sqlite3.connect("bilheteria.db")
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
        cur.execute("SELECT 1 FROM users WHERE username=?", ("funcionario1",))
        if not cur.fetchone():
            password = "123456".encode()
            cur.execute("INSERT INTO users(username,password_hash,role) VALUES (?,?,?)",
                        ("funcionario1", 
                         bcrypt.hashpw(password, bcrypt.gensalt()), 
                         "operator"))
            print("Usuario padrao criado: funcionario1")
        
        con.commit()
        con.close()
        print("Banco de dados inicializado com sucesso!")
        return True
    except Exception as e:
        print(f"Erro ao inicializar banco: {e}")
        return False

def main():
    """Função principal de setup"""
    print("Configurando Sistema de Bilheteria - Museu Cais do Sertao")
    print("=" * 60)
    
    # Configuração
    if not install_dependencies():
        sys.exit(1)
    
    create_directories()
    
    if not init_database():
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("Configuracao concluida com sucesso!")
    print("\nProximos passos:")
    print("1. Teste a aplicacao web: python run_web.py")
    print("2. Acesse: http://127.0.0.1:8000")
    print("3. Para criar executavel: python build.py")
    print("\nCredenciais de login:")
    print("   Usuario: funcionario1")
    print("   Senha: 123456")
    print("\nSistema pronto para uso!")

if __name__ == "__main__":
    main()
