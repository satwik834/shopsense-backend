import sys
import os

# Add parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal, engine, Base
from app.models.vendor import Vendor
from app.models.customer import Customer
from app.models.product import Product
from app.models.transaction import Transaction

def seed_data():
    print("Re-creating clean database tables...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    print("Seeding sample vendors...")
    v1 = Vendor(name="Apex Electronics", store_name="Apex Tech Store", email="contact@apex.com", phone="123-456-7890", description="Consumer electronics vendor")
    v2 = Vendor(name="Urban Fashion", store_name="Urban Style", email="sales@urbanfashion.com", phone="987-654-3210", description="Trendy clothing and accessories")
    db.add_all([v1, v2])
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

    print("Data seeding completed successfully!")
    db.close()

if __name__ == "__main__":
    seed_data()
