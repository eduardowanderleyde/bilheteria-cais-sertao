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
    admin_username = os.getenv("ADMIN_USERNAME", "***REMOVED***")
    admin_password = os.getenv("ADMIN_PASSWORD", "***REMOVED***")
    
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
        
        # Create default users if they don't exist
        default_users = [
            ("gestora1", "gestora123", "gestora"),
            ("bilheteira1", "bilheteira123", "bilheteira"),
            ("bilheteira2", "bilheteira123", "bilheteira"),
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
        
        # Print login information
        print("\nLogin Information:")
        print(f"Admin: {admin_username} / {admin_password}")
        print("Gestora: gestora1 / gestora123")
        print("Bilheteira: bilheteira1 / bilheteira123")
        print("Bilheteira: bilheteira2 / bilheteira123")
        
    except Exception as e:
        print(f"Error creating users: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    seed_admin()
