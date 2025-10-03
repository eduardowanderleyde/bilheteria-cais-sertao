#!/usr/bin/env python3
"""Verificar usuário no banco"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import User

# Configurar banco
DATABASE_URL = "sqlite:///./bilheteria.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def check_user():
    """Verificar usuário ***REMOVED***"""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == "***REMOVED***").first()
        if user:
            print(f"Usuário encontrado: {user.username}")
            print(f"Role: {user.role}")
            print(f"Password hash type: {type(user.password_hash)}")
            print(f"Password hash length: {len(user.password_hash) if user.password_hash else 'None'}")
            print(f"Password hash preview: {str(user.password_hash)[:50]}...")
            print(f"Is active: {user.is_active}")
        else:
            print("Usuário ***REMOVED*** não encontrado")
            
        # Listar todos os usuários
        users = db.query(User).all()
        print(f"\nTotal de usuários: {len(users)}")
        for u in users:
            print(f"- {u.username} (role: {u.role}, active: {u.is_active})")
            
    finally:
        db.close()

if __name__ == "__main__":
    check_user()
