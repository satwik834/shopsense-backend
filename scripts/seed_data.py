import sys
import os

# Add parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal, Base, engine
from app.core.security import hash_password
from app.models.enums import UserRole, ApprovalStatus
from app.models.admin import Admin
from app.models.vendor import Vendor
from app.models.customer import Customer
from app.models.product import Product
from app.models.transaction import Transaction

def seed_database():
    """Seed initial database with Admin, Vendors, Customers across RFM segments, Low Stock Products, and Transactions."""
    print("Re-creating database schema...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        print("Seeding Admin account...")
        admin = Admin(
            name="System Administrator",
            email="admin@shopsense.com",
            hashed_password=hash_password("adminpassword123"),
            role=UserRole.ADMIN
        )
        db.add(admin)

        print("Seeding Vendors...")
        vendor1 = Vendor(
            name="Apex Electronics",
            store_name="Apex Electronics Store",
            email="contact@apex.com",
            hashed_password=hash_password("vendorpass123"),
            phone="+91-9876543210",
            description="Premium consumer electronics, audio gear, and smart home tech.",
            role=UserRole.VENDOR,
            approval_status=ApprovalStatus.APPROVED,
            is_active=True
        )

        vendor2 = Vendor(
            name="Urban Fashion House",
            store_name="Urban Outfitters",
            email="sales@urbanfashion.com",
            hashed_password=hash_password("vendorpass123"),
            phone="+91-9876543211",
            description="Modern streetwear, luxury apparel, and designer accessories.",
            role=UserRole.VENDOR,
            approval_status=ApprovalStatus.APPROVED,
            is_active=True
        )

        vendor_pending = Vendor(
            name="Fresh Foods Organic",
            store_name="Organic Market",
            email="apply@freshfoods.com",
            hashed_password=hash_password("vendorpass123"),
            phone="+91-9876543212",
            description="Organic farm produce and healthy groceries.",
            role=UserRole.VENDOR,
            approval_status=ApprovalStatus.PENDING,
            is_active=False
        )

        db.add_all([vendor1, vendor2, vendor_pending])
        db.commit()

        print("Seeding Customers across segmentation tiers...")
        # 1. VIP Customer (High lifetime spend)
        c_vip1 = Customer(
            name="Ananya Sharma",
            email="ananya.sharma@example.com",
            phone="+91-9811223344",
            address="702 Prestige Towers, Bangalore, Karnataka"
        )
        # 2. VIP Customer
        c_vip2 = Customer(
            name="Rahul Verma",
            email="rahul.verma@example.com",
            phone="+91-9822334455",
            address="14 Palm Grove, Bandra, Mumbai"
        )
        # 3. Regular Customer
        c_reg1 = Customer(
            name="Priya Patel",
            email="priya.patel@example.com",
            phone="+91-9833445566",
            address="56 Navrangpura, Ahmedabad, Gujarat"
        )
        # 4. New Customer
        c_new1 = Customer(
            name="Aditya Kumar",
            email="aditya.kumar@example.com",
            phone="+91-9844556677",
            address="204 Cyber City, Hyderabad, Telangana"
        )
        # 5. Inactive Customer (0 purchases)
        c_inact1 = Customer(
            name="Kavita Rao",
            email="kavita.rao@example.com",
            phone="+91-9855667788",
            address="88 Anna Nagar, Chennai, Tamil Nadu"
        )

        db.add_all([c_vip1, c_vip2, c_reg1, c_new1, c_inact1])
        db.commit()

        print("Seeding Products with varied stock levels...")
        # In-Stock Products
        p1 = Product(
            vendor_id=vendor1.id,
            name="Wireless Noise-Canceling Headphones",
            description="Active noise cancellation, 30-hour battery life, spatial audio.",
            price=299.99,
            stock_quantity=45,
            category="Electronics",
            sku="APX-WHP-01"
        )
        p2 = Product(
            vendor_id=vendor1.id,
            name="4K Ultra HD Smart TV",
            description="55-inch OLED display, HDR10+, Dolby Atmos sound system.",
            price=649.00,
            stock_quantity=18,
            category="Electronics",
            sku="APX-TV-4K"
        )
        p3 = Product(
            vendor_id=vendor2.id,
            name="Premium Leather Jacket",
            description="Handcrafted genuine lambskin leather jacket with silk lining.",
            price=189.50,
            stock_quantity=28,
            category="Apparel",
            sku="UFH-LJK-02"
        )
        p4 = Product(
            vendor_id=vendor2.id,
            name="Classic Denim Overshirt",
            description="100% Japanese raw denim, tailored relaxed fit.",
            price=79.00,
            stock_quantity=40,
            category="Apparel",
            sku="UFH-DNM-04"
        )
        
        # Low Stock Products (Triggers Low Stock Alert <= 10)
        p_low1 = Product(
            vendor_id=vendor1.id,
            name="Mechanical Gaming Keyboard",
            description="Hot-swappable RGB mechanical keyboard with tactile switches.",
            price=129.99,
            stock_quantity=4,
            category="Electronics",
            sku="APX-KBD-RGB"
        )
        p_low2 = Product(
            vendor_id=vendor2.id,
            name="Italian Suede Chelsea Boots",
            description="Premium suede boots with Goodyear welted leather sole.",
            price=220.00,
            stock_quantity=2,
            category="Apparel",
            sku="UFH-BOT-05"
        )

        # Out of Stock Product (0 units)
        p_out1 = Product(
            vendor_id=vendor1.id,
            name="Smart Fitness Tracker Band",
            description="Continuous heart rate & SpO2 tracking with AMOLED display.",
            price=49.99,
            stock_quantity=0,
            category="Fitness",
            sku="APX-FIT-07"
        )

        db.add_all([p1, p2, p3, p4, p_low1, p_low2, p_out1])
        db.commit()

        print("Seeding Transactions for Segmentation & Recommendations...")
        tx_list = [
            # Ananya (VIP Spender - High Value)
            Transaction(customer_id=c_vip1.id, vendor_id=vendor1.id, product_id=p2.id, quantity=1, unit_price=649.00, total_amount=649.00, status="completed"),
            Transaction(customer_id=c_vip1.id, vendor_id=vendor1.id, product_id=p1.id, quantity=1, unit_price=299.99, total_amount=299.99, status="completed"),
            Transaction(customer_id=c_vip1.id, vendor_id=vendor1.id, product_id=p_low1.id, quantity=2, unit_price=129.99, total_amount=259.98, status="completed"),
            
            # Rahul (VIP Spender - Apparel & High Value)
            Transaction(customer_id=c_vip2.id, vendor_id=vendor2.id, product_id=p3.id, quantity=2, unit_price=189.50, total_amount=379.00, status="completed"),
            Transaction(customer_id=c_vip2.id, vendor_id=vendor2.id, product_id=p_low2.id, quantity=1, unit_price=220.00, total_amount=220.00, status="completed"),

            # Priya (Regular Customer)
            Transaction(customer_id=c_reg1.id, vendor_id=vendor2.id, product_id=p4.id, quantity=2, unit_price=79.00, total_amount=158.00, status="completed"),
            Transaction(customer_id=c_reg1.id, vendor_id=vendor1.id, product_id=p_out1.id, quantity=1, unit_price=49.99, total_amount=49.99, status="completed"),

            # Aditya (New Customer)
            Transaction(customer_id=c_new1.id, vendor_id=vendor2.id, product_id=p4.id, quantity=1, unit_price=79.00, total_amount=79.00, status="completed")
        ]

        db.add_all(tx_list)
        db.commit()

        print("Database re-seeded successfully for Milestone 2!")
        print("\nSeed Account Credentials:")
        print("  Admin User:   admin@shopsense.com / adminpassword123")
        print("  Vendor 1:     contact@apex.com / vendorpass123 (APPROVED)")
        print("  Vendor 2:     sales@urbanfashion.com / vendorpass123 (APPROVED)")
        print("  Vendor 3:     apply@freshfoods.com / vendorpass123 (PENDING)")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
