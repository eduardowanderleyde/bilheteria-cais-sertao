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
# IMPORTANTE: Altere estas credenciais antes de usar em produção!
ADMIN_USERNAME=admin
ADMIN_PASSWORD=CHANGE_ME_SECURE_PASSWORD_123!

# Application Settings
DEBUG=True
HOST=127.0.0.1
PORT=8000
"""
    
    with open(".env", "w") as f:
        f.write(env_content)
    
    print("Arquivo .env criado")
    print(f"SECRET_KEY gerada: {generate_secret_key()[:8]}...")

def setup_postgres_env():
    """Configura variáveis para PostgreSQL"""
    print("\nPara usar PostgreSQL, configure:")
    print("export DATABASE_URL=postgresql://user:password@localhost:5432/bilheteria")
    print("export ADMIN_USERNAME=admin")
    print("export ADMIN_PASSWORD='SUA_SENHA_SEGURA_AQUI'")
    print("export GESTORA_PASSWORD='SENHA_GESTORA_SEGURA'")
    print("export BILHETEIRA_PASSWORD='SENHA_BILHETEIRA_SEGURA'")
    print("export TEST_PASSWORD='SENHA_PARA_TESTES'")

def main():
    """Função principal"""
    print("Configurando variaveis de ambiente...")
    
    # Cria .env se não existir
    if not Path(".env").exists():
        create_env_file()
    else:
        print("Arquivo .env ja existe")
    
    # Mostra instruções para PostgreSQL
    setup_postgres_env()
    
    print("\nProximos passos:")
    print("1. Edite .env com suas configuracoes")
    print("2. Para PostgreSQL: configure DATABASE_URL")
    print("3. Execute: python seed_admin.py")
    print("4. Execute: uvicorn app.main:app --reload")

if __name__ == "__main__":
    main()
