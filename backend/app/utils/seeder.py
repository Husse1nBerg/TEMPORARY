"""
Database seeder to populate initial data
Path: backend/app/utils/seeder.py
Usage: python -m app.utils.seeder
"""

import json
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from app.database import SessionLocal, init_db
from app.models.user import User
from app.models.product import Product
from app.models.store import Store
from app.api.auth import get_password_hash

def seed_database():
    """Seed the database with initial data"""
    db = SessionLocal()
    
    try:
        # Initialize database tables
        init_db()
        print("✅ Database tables created")
        
        # Seed admin user
        admin_exists = db.query(User).filter(User.email == "admin@cropsegypt.com").first()
        if not admin_exists:
            admin = User(
                email="admin@cropsegypt.com",
                username="admin",
                hashed_password=get_password_hash("admin123456"),
                full_name="System Administrator",
                is_active=True,
                is_superuser=True
            )
            db.add(admin)
            print("✅ Admin user created (admin@cropsegypt.com / admin123456)")
        
        # Seed demo user
        demo_exists = db.query(User).filter(User.email == "demo@cropsegypt.com").first()
        if not demo_exists:
            demo = User(
                email="demo@cropsegypt.com",
                username="demo",
                hashed_password=get_password_hash("demo123456"),
                full_name="Demo User",
                is_active=True,
                is_superuser=False
            )
            db.add(demo)
            print("✅ Demo user created (demo@cropsegypt.com / demo123456)")
        
        # Seed stores
        with open("database/seeds/stores.json", "r") as f:
            stores_data = json.load(f)
        
        for store_data in stores_data:
            exists = db.query(Store).filter(Store.name == store_data["name"]).first()
            if not exists:
                store = Store(**store_data)
                db.add(store)
        print(f"✅ {len(stores_data)} stores seeded")
        
        # Seed products
        with open("database/seeds/products.json", "r") as f:
            products_data = json.load(f)
        
        for product_data in products_data:
            exists = db.query(Product).filter(Product.name == product_data["name"]).first()
            if not exists:
                # Convert keywords list to JSON string
                product_data["keywords"] = json.dumps(product_data.get("keywords", []))
                product = Product(**product_data)
                db.add(product)
        print(f"✅ {len(products_data)} products seeded")
        
        # Commit all changes
        db.commit()
        print("\n🎉 Database seeding completed successfully!")
        
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()