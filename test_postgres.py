#!/usr/bin/env python3
"""Teste de conexão com PostgreSQL do Render"""

def test_connection():
    try:
        from app.db import engine
        print("Testando conexão com PostgreSQL...")
        with engine.connect() as conn:
            from sqlalchemy import text
            result = conn.execute(text("SELECT 1"))
            print("✅ Conexão com PostgreSQL OK!")
            return True
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
        return False

def create_tables():
    try:
        from app.db import Base, engine
        print("Criando tabelas no PostgreSQL...")
        Base.metadata.create_all(bind=engine)
        print("✅ Tabelas criadas com sucesso!")
        return True
    except Exception as e:
        print(f"❌ Erro ao criar tabelas: {e}")
        return False

def seed_users():
    try:
        import subprocess
        import sys
        import os
        
        # Define variáveis de ambiente
        env = os.environ.copy()
        env['ADMIN_USERNAME'] = '***REMOVED***'
        env['ADMIN_PASSWORD'] = '***REMOVED***'
        
        print("Criando usuários no PostgreSQL...")
        result = subprocess.run([sys.executable, 'seed_admin.py'], 
                              env=env, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Usuários criados com sucesso!")
            print(result.stdout)
            return True
        else:
            print(f"❌ Erro ao criar usuários: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao executar seed: {e}")
        return False

if __name__ == "__main__":
    print("🐘 Configurando PostgreSQL do Render")
    print("=" * 50)
    
    if test_connection():
        if create_tables():
            if seed_users():
                print("\n🎉 Configuração concluída com sucesso!")
                print("\n📋 Próximos passos:")
                print("1. Execute: uvicorn app.main:app --reload")
                print("2. Acesse: http://127.0.0.1:8000")
                print("3. Login: ***REMOVED*** / ***REMOVED***")
            else:
                print("❌ Falha ao criar usuários")
        else:
            print("❌ Falha ao criar tabelas")
    else:
        print("❌ Falha na conexão com PostgreSQL")
