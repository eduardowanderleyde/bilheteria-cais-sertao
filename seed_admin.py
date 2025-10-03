"""Script to seed admin user from environment variables"""
import os
import sys
from sqlalchemy.orm import Session
from app.db import SessionLocal, engine
from app.models import User, Base
from app.auth import hash_password

def seed_admin():
    """Create admin user from environment variables"""
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    # Get admin credentials from environment
    admin_username = os.getenv("ADMIN_USERNAME")
    admin_password = os.getenv("ADMIN_PASSWORD")
    
    if not admin_username or not admin_password:
        print("ERRO: ADMIN_USERNAME e ADMIN_PASSWORD devem ser definidos nas variáveis de ambiente")
        print("Exemplo: export ADMIN_USERNAME=admin && export ADMIN_PASSWORD=senha_segura")
        sys.exit(1)
    
    db = SessionLocal()
    try:
        # Check if admin user already exists
        existing_admin = db.query(User).filter(User.username == admin_username).first()
        
        if existing_admin:
            print(f"Admin user '{admin_username}' already exists. Updating password...")
            existing_admin.password_hash = hash_password(admin_password)
            existing_admin.role = "admin"
            existing_admin.is_active = True
        else:
            print(f"Creating admin user '{admin_username}'...")
            admin_user = User(
                username=admin_username,
                password_hash=hash_password(admin_password),
                role="admin",
                is_active=True
            )
            db.add(admin_user)
        
        # Create default users if they don't exist (using environment variables)
        gestora_password = os.getenv("GESTORA_PASSWORD", "gestora123")
        bilheteira_password = os.getenv("BILHETEIRA_PASSWORD", "bilheteira123")
        
        default_users = [
            ("gestora1", gestora_password, "gestora"),
            ("bilheteira1", bilheteira_password, "bilheteira"),
            ("bilheteira2", bilheteira_password, "bilheteira"),
        ]
        
        for username, password, role in default_users:
            existing_user = db.query(User).filter(User.username == username).first()
            if not existing_user:
                print(f"Creating {role} user '{username}'...")
                user = User(
                    username=username,
                    password_hash=hash_password(password),
                    role=role,
                    is_active=True
                )
                db.add(user)
        
        db.commit()
        print("Users created/updated successfully!")
        
        # Print login information (without passwords)
        print("\nUsers created successfully!")
        print(f"Admin: {admin_username}")
        print("Gestora: gestora1")
        print("Bilheteira: bilheteira1, bilheteira2")
        print("\nPasswords are stored securely in environment variables.")
        
    except Exception as e:
        print(f"Error creating users: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    seed_admin()
