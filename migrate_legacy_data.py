"""Script to migrate legacy sales data to new structure"""
import sqlite3
from sqlalchemy.orm import Session
from app.db import SessionLocal, engine
from app.models import User, Order, OrderItem, Base
from app.auth import hash_password
from datetime import datetime

def migrate_legacy_data():
    """Migrate data from legacy sales table to new structure"""
    print("🔄 Starting migration of legacy data...")
    
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    # Connect to legacy database
    legacy_db = sqlite3.connect("bilheteria.db")
    legacy_cursor = legacy_db.cursor()
    
    # Get current database session
    db = SessionLocal()
    
    try:
        # Check if legacy sales table exists
        legacy_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sales'")
        if not legacy_cursor.fetchone():
            print("❌ Legacy sales table not found. Nothing to migrate.")
            return
        
        # Get legacy sales data
        legacy_cursor.execute("""
            SELECT sold_at, ticket_type, qty, unit_price_cents, operator_username, 
                   name, state, city, note, payment_method
            FROM sales
            ORDER BY sold_at
        """)
        sales_data = legacy_cursor.fetchall()
        
        if not sales_data:
            print("ℹ️ No sales data found in legacy table.")
            return
        
        print(f"📊 Found {len(sales_data)} legacy sales records")
        
        # Create default user if not exists
        default_user = db.query(User).filter(User.username == "migrated").first()
        if not default_user:
            default_user = User(
                username="migrated",
                password_hash=hash_password("migrated123"),
                role="bilheteira",
                is_active=True
            )
            db.add(default_user)
            db.flush()
        
        # Migrate each sale
        migrated_count = 0
        for sale in sales_data:
            sold_at, ticket_type, qty, unit_price_cents, operator_username, name, state, city, note, payment_method = sale
            
            # Create order
            order = Order(
                created_at=datetime.fromisoformat(sold_at) if sold_at else datetime.now(),
                user_id=default_user.id,
                channel="balcao",
                payment_method=payment_method or "credito",
                state=state,
                city=city,
                note=note
            )
            db.add(order)
            db.flush()
            
            # Create order item
            order_item = OrderItem(
                order_id=order.id,
                ticket_type=ticket_type,
                qty=qty,
                unit_price_cents=unit_price_cents,
                discount_reason=None  # Legacy data doesn't have discount reasons
            )
            db.add(order_item)
            
            migrated_count += 1
        
        db.commit()
        print(f"✅ Successfully migrated {migrated_count} sales records")
        
        # Optional: Mark legacy table as migrated
        legacy_cursor.execute("ALTER TABLE sales ADD COLUMN migrated INTEGER DEFAULT 0")
        legacy_cursor.execute("UPDATE sales SET migrated = 1")
        legacy_db.commit()
        
        print("🎉 Migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        db.rollback()
        raise
    finally:
        legacy_db.close()
        db.close()

if __name__ == "__main__":
    migrate_legacy_data()
