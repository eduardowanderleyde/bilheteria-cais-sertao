#!/usr/bin/env python3
"""
Script para configurar variáveis de ambiente
Uso: python setup_env.py
"""
import os
import secrets
from pathlib import Path

def generate_secret_key():
    """Gera uma chave secreta segura"""
    return secrets.token_hex(32)

def create_env_file():
    """Cria arquivo .env com configurações"""
    env_content = f"""# Database Configuration
DATABASE_URL=sqlite:///./bilheteria.db
# Para PostgreSQL: DATABASE_URL=postgresql://user:password@localhost:5432/bilheteria

# Security
SECRET_KEY={generate_secret_key()}

# Admin User (created by seed_admin.py)
ADMIN_USERNAME=***REMOVED***
ADMIN_PASSWORD=***REMOVED***

# Application Settings
DEBUG=True
HOST=127.0.0.1
PORT=8000
"""
    
    with open(".env", "w") as f:
        f.write(env_content)
    
    print("✅ Arquivo .env criado")
    print(f"🔑 SECRET_KEY gerada: {generate_secret_key()[:8]}...")

def setup_postgres_env():
    """Configura variáveis para PostgreSQL"""
    print("\n🐘 Para usar PostgreSQL, configure:")
    print("export DATABASE_URL=postgresql://user:password@localhost:5432/bilheteria")
    print("export ADMIN_USERNAME=***REMOVED***")
    print("export ADMIN_PASSWORD='***REMOVED***'")

def main():
    """Função principal"""
    print("🔧 Configurando variáveis de ambiente...")
    
    # Cria .env se não existir
    if not Path(".env").exists():
        create_env_file()
    else:
        print("ℹ️ Arquivo .env já existe")
    
    # Mostra instruções para PostgreSQL
    setup_postgres_env()
    
    print("\n📋 Próximos passos:")
    print("1. Edite .env com suas configurações")
    print("2. Para PostgreSQL: configure DATABASE_URL")
    print("3. Execute: python seed_admin.py")
    print("4. Execute: uvicorn app.main:app --reload")

if __name__ == "__main__":
    main()
