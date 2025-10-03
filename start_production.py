#!/usr/bin/env python3
"""
Script de inicialização para produção
Uso: python start_production.py
"""
import os
import sys
import subprocess
from pathlib import Path

def check_requirements():
    """Verifica se os requisitos estão instalados"""
    try:
        import fastapi
        import uvicorn
        import sqlalchemy
        import pandas
        print("✅ Dependências Python OK")
        return True
    except ImportError as e:
        print(f"❌ Dependência faltando: {e}")
        print("Execute: pip install -r requirements.txt")
        return False

def check_env_vars():
    """Verifica variáveis de ambiente"""
    required_vars = ["SECRET_KEY"]
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Variáveis faltando: {', '.join(missing_vars)}")
        print("Execute: python setup_env.py")
        return False
    
    print("✅ Variáveis de ambiente OK")
    return True

def check_database():
    """Verifica conexão com banco"""
    try:
        from app.db import engine
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        print("✅ Conexão com banco OK")
        return True
    except Exception as e:
        print(f"❌ Erro de conexão com banco: {e}")
        return False

def create_tables():
    """Cria tabelas se não existirem"""
    try:
        from app.db import Base, engine
        Base.metadata.create_all(bind=engine)
        print("✅ Tabelas criadas/verificadas")
        return True
    except Exception as e:
        print(f"❌ Erro ao criar tabelas: {e}")
        return False

def seed_users():
    """Cria usuários iniciais"""
    try:
        from seed_admin import seed_admin
        seed_admin()
        print("✅ Usuários criados")
        return True
    except Exception as e:
        print(f"❌ Erro ao criar usuários: {e}")
        return False

def start_server():
    """Inicia o servidor"""
    try:
        print("🚀 Iniciando servidor...")
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "app.main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000",
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\n👋 Servidor parado")
    except Exception as e:
        print(f"❌ Erro ao iniciar servidor: {e}")

def main():
    """Função principal"""
    print("🎫 Sistema de Bilheteria - Inicialização")
    print("=" * 50)
    
    # Verificações
    checks = [
        ("Dependências", check_requirements),
        ("Variáveis de ambiente", check_env_vars),
        ("Conexão com banco", check_database),
        ("Tabelas", create_tables),
        ("Usuários", seed_users),
    ]
    
    for check_name, check_func in checks:
        print(f"\n🔍 Verificando: {check_name}")
        if not check_func():
            print(f"❌ Falha em: {check_name}")
            print("Corrija o problema e execute novamente")
            return
    
    print("\n✅ Todas as verificações passaram!")
    print("\n🌐 Acesse: http://127.0.0.1:8000")
    print("👤 Login: ***REMOVED*** / ***REMOVED***")
    
    # Inicia servidor
    start_server()

if __name__ == "__main__":
    main()
