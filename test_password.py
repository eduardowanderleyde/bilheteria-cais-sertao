#!/usr/bin/env python3
"""Testar senha do usuário ***REMOVED***"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import User
import bcrypt

# Configurar banco
DATABASE_URL = "sqlite:///./bilheteria.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def test_password():
    """Testar senhas para ***REMOVED***"""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == "***REMOVED***").first()
        if not user:
            print("Usuário não encontrado")
            return
            
        print(f"Testando senhas para usuário: {user.username}")
        print(f"Hash armazenado: {user.password_hash}")
        
        # Testar diferentes senhas
        passwords_to_test = [
            "***REMOVED***",
            "18091992123", 
            "admin",
            "password",
            "123456"
        ]
        
        for pwd in passwords_to_test:
            try:
                result = bcrypt.checkpw(pwd.encode("utf-8"), user.password_hash)
                print(f"Senha '{pwd}': {'OK' if result else 'FALHOU'}")
            except Exception as e:
                print(f"Senha '{pwd}': ERRO - {e}")
                
    finally:
        db.close()

if __name__ == "__main__":
    test_password()
