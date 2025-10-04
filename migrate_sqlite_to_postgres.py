#!/usr/bin/env python3
"""
Script para migrar dados do SQLite para PostgreSQL
Uso: python migrate_sqlite_to_postgres.py
"""
import os
import sqlite3
import pandas as pd
from sqlalchemy import create_engine, text
from app.db import SessionLocal
from app.models import User, Order, OrderItem, Group, OrderEvent, Sale
from app.auth import hash_password
from datetime import datetime

def export_sqlite_to_csv():
    """Exporta dados do SQLite para CSV"""
    print("📤 Exportando dados do SQLite...")
    
    # Conecta ao SQLite
    sqlite_conn = sqlite3.connect("bilheteria.db")
    
    # Exporta users
    users_df = pd.read_sql_query("SELECT * FROM users", sqlite_conn)
    users_df.to_csv("users_export.csv", index=False)
    print(f"✅ Exportados {len(users_df)} usuários")
    
    # Exporta sales
    sales_df = pd.read_sql_query("SELECT * FROM sales", sqlite_conn)
    sales_df.to_csv("sales_export.csv", index=False)
    print(f"✅ Exportados {len(sales_df)} vendas")
    
    sqlite_conn.close()
    return users_df, sales_df

def migrate_to_postgres(users_df, sales_df):
    """Migra dados para PostgreSQL"""
    print("📥 Migrando dados para PostgreSQL...")
    
    # Conecta ao PostgreSQL
    db = SessionLocal()
    
    try:
        # Migra usuários
        for _, user_row in users_df.iterrows():
            # Verifica se usuário já existe
            existing_user = db.query(User).filter(User.username == user_row['username']).first()
            if not existing_user:
                user = User(
                    username=user_row['username'],
                    password_hash=user_row['password_hash'],
                    role=user_row.get('role', 'bilheteira'),
                    is_active=bool(user_row.get('is_active', True))
                )
                db.add(user)
        
        db.commit()
        print("✅ Usuários migrados")
        
        # Migra vendas (converte para nova estrutura)
        for _, sale_row in sales_df.iterrows():
            # Busca usuário
            user = db.query(User).filter(User.username == sale_row['operator_username']).first()
            if not user:
                # Cria usuário padrão se não existir
                user = User(
                    username=sale_row['operator_username'],
                    password_hash=hash_password("migrated123"),
                    role="bilheteira",
                    is_active=True
                )
                db.add(user)
                db.flush()
            
            # Cria order
            order = Order(
                created_at=datetime.fromisoformat(sale_row['sold_at']) if sale_row['sold_at'] else datetime.now(),
                user_id=user.id,
                channel="balcao",
                payment_method=sale_row.get('payment_method', 'credito'),
                state=sale_row.get('state'),
                city=sale_row.get('city'),
                note=sale_row.get('note')
            )
            db.add(order)
            db.flush()
            
            # Cria order item
            order_item = OrderItem(
                order_id=order.id,
                ticket_type=sale_row['ticket_type'],
                qty=sale_row['qty'],
                unit_price_cents=sale_row['unit_price_cents'],
                discount_reason=None  # Legacy data não tem motivos
            )
            db.add(order_item)
        
        db.commit()
        print("✅ Vendas migradas")
        
        # Cria usuários padrão se não existirem
        default_users = [
            ("admingeral", "18091992123", "admin"),
            ("keila", "Januario76", "gestora"),
            ("Evelyn", "Januario 76", "gestora"),
            ("bilheteira1", "Januario72", "bilheteira"),
            ("bilheteira2", "Januario72", "bilheteira"),
        ]
        
        for username, password, role in default_users:
            existing = db.query(User).filter(User.username == username).first()
            if not existing:
                user = User(
                    username=username,
                    password_hash=hash_password(password),
                    role=role,
                    is_active=True
                )
                db.add(user)
        
        db.commit()
        print("✅ Usuários padrão criados")
        
    except Exception as e:
        print(f"❌ Erro na migração: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def cleanup_csv_files():
    """Remove arquivos CSV temporários"""
    for file in ["users_export.csv", "sales_export.csv"]:
        if os.path.exists(file):
            os.remove(file)
            print(f"🗑️ Removido {file}")

def main():
    """Função principal"""
    print("🚀 Iniciando migração SQLite → PostgreSQL")
    
    # Verifica se arquivo SQLite existe
    if not os.path.exists("bilheteria.db"):
        print("❌ Arquivo bilheteria.db não encontrado")
        return
    
    # Verifica variável de ambiente
    if not os.getenv("DATABASE_URL"):
        print("❌ Variável DATABASE_URL não configurada")
        print("Configure: export DATABASE_URL=postgresql://user:pass@host:port/db")
        return
    
    try:
        # Exporta dados
        users_df, sales_df = export_sqlite_to_csv()
        
        # Migra para PostgreSQL
        migrate_to_postgres(users_df, sales_df)
        
        # Limpa arquivos temporários
        cleanup_csv_files()
        
        print("🎉 Migração concluída com sucesso!")
        print("\n📋 Próximos passos:")
        print("1. Teste o login com os usuários migrados")
        print("2. Verifique se os dados estão corretos")
        print("3. Configure backup do PostgreSQL")
        
    except Exception as e:
        print(f"❌ Erro durante migração: {e}")
        cleanup_csv_files()

if __name__ == "__main__":
    main()
