import sys
import os

# Add parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal, engine, Base
from app.core.security import hash_password
from app.models.enums import UserRole, ApprovalStatus
from app.models.admin import Admin
from app.models.vendor import Vendor
from app.models.customer import Customer
from app.models.product import Product
from app.models.transaction import Transaction

def seed_data():
    print("Re-creating clean database tables...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    print("Seeding default Admin user...")
    admin_user = Admin(
        name="System Administrator",
        email="admin@shopsense.com",
        hashed_password=hash_password("adminpassword123"),
        role=UserRole.ADMIN,
        is_active=True
    )
    db.add(admin_user)
    db.commit()

    print("Seeding approved vendors...")
    v1 = Vendor(
        name="Apex Electronics",
        store_name="Apex Tech Store",
        email="contact@apex.com",
        hashed_password=hash_password("vendorpass123"),
        phone="123-456-7890",
        description="Consumer electronics vendor",
        role=UserRole.VENDOR,
        approval_status=ApprovalStatus.APPROVED,
        is_active=True
    )
    v2 = Vendor(
        name="Urban Fashion",
        store_name="Urban Style",
        email="sales@urbanfashion.com",
        hashed_password=hash_password("vendorpass123"),
        phone="987-654-3210",
        description="Trendy clothing and accessories",
        role=UserRole.VENDOR,
        approval_status=ApprovalStatus.APPROVED,
        is_active=True
    )

    print("Seeding a PENDING vendor application...")
    v3 = Vendor(
        name="Fresh Foods Inc.",
        store_name="Fresh Organics",
        email="apply@freshfoods.com",
        hashed_password=hash_password("vendorpass123"),
        phone="555-9988",
        description="Organic groceries vendor application",
        role=UserRole.VENDOR,
        approval_status=ApprovalStatus.PENDING,
        is_active=True
    )

    db.add_all([v1, v2, v3])
    db.commit()

    print("Seeding sample customers...")
    c1 = Customer(name="Alice Johnson", email="alice@gmail.com", phone="555-0101", address="123 Main St")
    c2 = Customer(name="Bob Smith", email="bob@gmail.com", phone="555-0202", address="456 Elm St")
    db.add_all([c1, c2])
    db.commit()

    print("Seeding sample products...")
    p1 = Product(vendor_id=v1.id, name="Wireless Headphones", price=99.99, stock_quantity=50, category="Electronics", sku="APX-WHP-01")
    p2 = Product(vendor_id=v1.id, name="Mechanical Keyboard", price=149.50, stock_quantity=30, category="Electronics", sku="APX-MKB-02")
    p3 = Product(vendor_id=v2.id, name="Denim Jacket", price=79.99, stock_quantity=40, category="Apparel", sku="URB-DJK-01")
    db.add_all([p1, p2, p3])
    db.commit()

    print("Seeding sample transactions...")
    t1 = Transaction(customer_id=c1.id, vendor_id=v1.id, product_id=p1.id, quantity=2, unit_price=p1.price, total_amount=199.98, status="completed")
    t2 = Transaction(customer_id=c2.id, vendor_id=v1.id, product_id=p2.id, quantity=1, unit_price=p2.price, total_amount=149.50, status="completed")
    t3 = Transaction(customer_id=c1.id, vendor_id=v2.id, product_id=p3.id, quantity=3, unit_price=p3.price, total_amount=239.97, status="completed")
    db.add_all([t1, t2, t3])
    db.commit()

    print("\nData seeding completed successfully!")
    print("Default Admin Account: admin@shopsense.com / adminpassword123")
    print("Approved Vendor Account: contact@apex.com / vendorpass123")
    print("Pending Vendor Account: apply@freshfoods.com / vendorpass123")

    db.close()

if __name__ == "__main__":
    seed_data()
