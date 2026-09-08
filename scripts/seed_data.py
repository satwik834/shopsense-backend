import sys
import os
from datetime import datetime, timedelta

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
    """Seed database with realistic multi-vendor products, customer profiles, and 30-day transactions."""
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

        print("Seeding Approved & Pending Vendors...")
        vendor1 = Vendor(
            name="Apex Electronics",
            store_name="Apex Electronics Store",
            email="contact@apex.com",
            hashed_password=hash_password("vendorpass123"),
            phone="+91-9876543210",
            description="Premium consumer electronics, laptops, audio gear, and smart home tech.",
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
            description="Modern streetwear, luxury leather apparel, and designer footwear.",
            role=UserRole.VENDOR,
            approval_status=ApprovalStatus.APPROVED,
            is_active=True
        )

        vendor3 = Vendor(
            name="FitTech Pro Gear",
            store_name="FitTech Store",
            email="support@fittech.com",
            hashed_password=hash_password("vendorpass123"),
            phone="+91-9876543213",
            description="Professional workout equipment and smart fitness trackers.",
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

        db.add_all([vendor1, vendor2, vendor3, vendor_pending])
        db.commit()

        print("Seeding Customers across RFM segmentation tiers...")
        c_vip1 = Customer(name="Ananya Sharma", email="ananya.sharma@example.com", phone="+91-9811223344", address="702 Prestige Towers, Bangalore")
        c_vip2 = Customer(name="Rahul Verma", email="rahul.verma@example.com", phone="+91-9822334455", address="14 Palm Grove, Mumbai")
        c_vip3 = Customer(name="Siddharth Malhotra", email="sid.malhotra@example.com", phone="+91-9833112233", address="99 Jubilee Hills, Hyderabad")
        c_reg1 = Customer(name="Priya Patel", email="priya.patel@example.com", phone="+91-9833445566", address="56 Navrangpura, Ahmedabad")
        c_reg2 = Customer(name="Vikram Singh", email="vikram.singh@example.com", phone="+91-9844112233", address="12 Civil Lines, Jaipur")
        c_new1 = Customer(name="Aditya Kumar", email="aditya.kumar@example.com", phone="+91-9844556677", address="204 Cyber City, Gurgaon")
        c_new2 = Customer(name="Sneha Reddy", email="sneha.reddy@example.com", phone="+91-9855112233", address="45 Park Street, Kolkata")
        c_inact1 = Customer(name="Kavita Rao", email="kavita.rao@example.com", phone="+91-9855667788", address="88 Anna Nagar, Chennai")
        c_inact2 = Customer(name="Rohan Gupta", email="rohan.gupta@example.com", phone="+91-9866112233", address="33 MG Road, Pune")

        db.add_all([c_vip1, c_vip2, c_vip3, c_reg1, c_reg2, c_new1, c_new2, c_inact1, c_inact2])
        db.commit()

        print("Seeding Products (including Laptops, Headphones, TVs, Jackets, Boots, and Fitness gear)...")
        # Electronics
        p1 = Product(vendor_id=vendor1.id, name="Pro Ultrabook 15-inch Laptop", description="Intel i7 processor, 16GB RAM, 512GB SSD, 15.6-inch Full HD display laptop for productivity and video editing.", price=999.00, stock_quantity=15, category="Electronics", sku="APX-LTP-15")
        p2 = Product(vendor_id=vendor1.id, name="Wireless Noise-Canceling Headphones", description="Active noise cancellation, 30-hour battery life, spatial audio.", price=299.99, stock_quantity=45, category="Electronics", sku="APX-WHP-01")
        p3 = Product(vendor_id=vendor1.id, name="4K Ultra HD Smart TV", description="55-inch OLED display, HDR10+, Dolby Atmos sound system.", price=649.00, stock_quantity=18, category="Electronics", sku="APX-TV-4K")
        p4 = Product(vendor_id=vendor1.id, name="Mechanical Gaming Keyboard", description="Hot-swappable RGB mechanical keyboard with tactile switches.", price=129.99, stock_quantity=4, category="Electronics", sku="APX-KBD-RGB")
        p5 = Product(vendor_id=vendor1.id, name="Ergonomic Wireless Mouse", description="Precision optical sensor with dual Bluetooth connection.", price=49.50, stock_quantity=35, category="Electronics", sku="APX-MSE-04")

        # Apparel
        p6 = Product(vendor_id=vendor2.id, name="Premium Leather Jacket", description="Handcrafted genuine lambskin leather jacket with silk lining.", price=189.50, stock_quantity=28, category="Apparel", sku="UFH-LJK-02")
        p7 = Product(vendor_id=vendor2.id, name="Classic Denim Overshirt", description="100% Japanese raw denim, relaxed tailored fit.", price=79.00, stock_quantity=40, category="Apparel", sku="UFH-DNM-04")
        p8 = Product(vendor_id=vendor2.id, name="Italian Suede Chelsea Boots", description="Premium suede boots with Goodyear welted leather sole.", price=220.00, stock_quantity=2, category="Apparel", sku="UFH-BOT-05")
        p9 = Product(vendor_id=vendor2.id, name="Organic Cotton Graphic Hoodie", description="Heavyweight 400gsm organic cotton hoodie.", price=65.00, stock_quantity=50, category="Apparel", sku="UFH-HD-08")

        # Fitness & Health
        p10 = Product(vendor_id=vendor3.id, name="Smart Fitness Tracker Band", description="Continuous heart rate & SpO2 tracking with AMOLED display.", price=49.99, stock_quantity=6, category="Fitness", sku="FIT-TRK-01")
        p11 = Product(vendor_id=vendor3.id, name="Adjustable Dumbbell Set 24kg", description="Compact dial-select weights for home workout.", price=299.00, stock_quantity=12, category="Fitness", sku="FIT-DBL-24")
        p12 = Product(vendor_id=vendor3.id, name="Non-Slip Yoga Mat Pro", description="6mm eco-friendly natural rubber workout mat.", price=35.00, stock_quantity=0, category="Fitness", sku="FIT-MAT-03")

        db.add_all([p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11, p12])
        db.commit()

        print("Seeding 30-Day Time-Stamped Transaction Matrix...")
        now = datetime.utcnow()
        tx_data = [
            # Day -28
            (c_vip1.id, vendor1.id, p1.id, 1, 999.00, now - timedelta(days=28)),
            (c_vip2.id, vendor2.id, p6.id, 2, 189.50, now - timedelta(days=27)),
            # Day -22
            (c_vip1.id, vendor1.id, p2.id, 1, 299.99, now - timedelta(days=22)),
            (c_vip3.id, vendor3.id, p11.id, 1, 299.00, now - timedelta(days=20)),
            # Day -15
            (c_reg1.id, vendor2.id, p7.id, 2, 79.00, now - timedelta(days=15)),
            (c_reg2.id, vendor3.id, p10.id, 1, 49.99, now - timedelta(days=14)),
            (c_vip2.id, vendor2.id, p8.id, 1, 220.00, now - timedelta(days=12)),
            # Day -8
            (c_vip1.id, vendor1.id, p4.id, 2, 129.99, now - timedelta(days=8)),
            (c_vip3.id, vendor1.id, p2.id, 1, 299.99, now - timedelta(days=7)),
            (c_new1.id, vendor2.id, p9.id, 1, 65.00, now - timedelta(days=5)),
            # Day -3
            (c_new2.id, vendor1.id, p5.id, 1, 49.50, now - timedelta(days=3)),
            (c_reg1.id, vendor3.id, p10.id, 1, 49.99, now - timedelta(days=2)),
            (c_vip2.id, vendor2.id, p9.id, 2, 65.00, now - timedelta(days=1))
        ]

        for c_id, v_id, pr_id, qty, price, t_date in tx_data:
            t_obj = Transaction(
                customer_id=c_id,
                vendor_id=v_id,
                product_id=pr_id,
                quantity=qty,
                unit_price=price,
                total_amount=qty * price,
                status="completed",
                transaction_date=t_date
            )
            db.add(t_obj)

        db.commit()
        print("Database successfully seeded with laptops, multi-vendor items, customer tiers, and 30-day transactions!")
        print("\nSeed Credentials:")
        print("  Admin User:   admin@shopsense.com / adminpassword123")
        print("  Vendor 1:     contact@apex.com / vendorpass123 (APPROVED)")
        print("  Vendor 2:     sales@urbanfashion.com / vendorpass123 (APPROVED)")
        print("  Vendor 3:     support@fittech.com / vendorpass123 (APPROVED)")
        print("  Vendor 4:     apply@freshfoods.com / vendorpass123 (PENDING)")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
