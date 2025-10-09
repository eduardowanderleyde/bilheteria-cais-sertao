"""Script to seed admin user from environment variables"""
import os
import sys
from sqlalchemy.orm import Session
from app.db import SessionLocal, engine
from app.models import User, Base
from app.auth import hash_password
from dotenv import load_dotenv

load_dotenv()  # carrega o .env da raiz

def seed_admin():
    """Create admin user from environment variables"""
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    # Get admin credentials from environment - REQUIRED, NO DEFAULTS
    admin_username = os.getenv("ADMIN_USERNAME")
    admin_password = os.getenv("ADMIN_PASSWORD")
    
    if not admin_username or not admin_password:
        print("❌ ERRO: ADMIN_USERNAME e ADMIN_PASSWORD são obrigatórios!")
        print("\nDefina as variáveis de ambiente antes de executar:")
        print("  export ADMIN_USERNAME=<seu_usuario>")
        print("  export ADMIN_PASSWORD=<SuaSenhaSegura123>")
        print("\nOu crie um arquivo .env na raiz do projeto:")
        print("  ADMIN_USERNAME=<seu_usuario>")
        print("  ADMIN_PASSWORD=<SuaSenhaSegura123>")
        sys.exit(1)
    
    # Validate password strength in production
    if len(admin_password) < 8:
        print("⚠️  AVISO: Senha do admin muito curta (mínimo 8 caracteres)")
        if os.getenv("ENV") == "production":
            print("❌ ERRO: Em produção, a senha deve ter no mínimo 8 caracteres")
            sys.exit(1)
    
    db = SessionLocal()
    try:
        # Check if admin user already exists
        existing_admin = db.query(User).filter(User.username == admin_username).first()
        
        if existing_admin:
            print(f"✓ Admin user '{admin_username}' já existe. Atualizando senha...")
            existing_admin.password_hash = hash_password(admin_password)
            existing_admin.role = "admin"
            existing_admin.is_active = True
        else:
            print(f"✓ Criando admin user '{admin_username}'...")
            admin_user = User(
                username=admin_username,
                password_hash=hash_password(admin_password),
                role="admin",
                is_active=True
            )
            db.add(admin_user)
        
        # Create default users ONLY if passwords are provided
        gestora_password = os.getenv("GESTORA_PASSWORD")
        bilheteira_password = os.getenv("BILHETEIRA_PASSWORD")
        
        default_users = []
        
        if gestora_password:
            default_users.append(("gestora1", gestora_password, "gestora"))
        
        if bilheteira_password:
            default_users.extend([
                ("bilheteira1", bilheteira_password, "bilheteira"),
                ("bilheteira2", bilheteira_password, "bilheteira"),
            ])
        
        for username, password, role in default_users:
            existing_user = db.query(User).filter(User.username == username).first()
            if not existing_user:
                print(f"✓ Criando {role} user '{username}'...")
                user = User(
                    username=username,
                    password_hash=hash_password(password),
                    role=role,
                    is_active=True
                )
                db.add(user)
            else:
                print(f"  {role} user '{username}' já existe (não atualizado)")
        
        db.commit()
        
        # Print summary (without passwords)
        print("\n" + "="*50)
        print("✓ Usuários criados/atualizados com sucesso!")
        print("="*50)
        print(f"\nAdmin: {admin_username}")
        
        if gestora_password:
            print("Gestora: gestora1")
        else:
            print("⚠️  Gestora não criada (defina GESTORA_PASSWORD)")
            
        if bilheteira_password:
            print("Bilheteiras: bilheteira1, bilheteira2")
        else:
            print("⚠️  Bilheteiras não criadas (defina BILHETEIRA_PASSWORD)")
        
        print("\n🔒 Senhas armazenadas com segurança (bcrypt hash)")
        print("="*50)
        
    except Exception as e:
        print(f"Error creating users: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    seed_admin()
