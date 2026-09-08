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
    """Seed database with accurate multi-vendor products, customer profiles, and 30-day transactions."""
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
            description="Premium consumer electronics, laptops, smartphones, 4K TVs, audio gear, and smart home devices.",
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
            description="Modern streetwear, luxury leather apparel, designer footwear, and accessories.",
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
            description="Professional workout equipment, smart fitness trackers, and athletic accessories.",
            role=UserRole.VENDOR,
            approval_status=ApprovalStatus.APPROVED,
            is_active=True
        )

        vendor4 = Vendor(
            name="Luxe Home Essentials",
            store_name="Luxe Living",
            email="hello@luxehome.com",
            hashed_password=hash_password("vendorpass123"),
            phone="+91-9876543214",
            description="High-end kitchen appliances, smart robotic vacuums, and home comfort solutions.",
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
            description="Organic farm produce and healthy gourmet foods.",
            role=UserRole.VENDOR,
            approval_status=ApprovalStatus.PENDING,
            is_active=False
        )

        db.add_all([vendor1, vendor2, vendor3, vendor4, vendor_pending])
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

        print("Seeding Expanded Products with Accurate Pricing...")
        products = [
            # Apex Electronics (Vendor 1)
            Product(vendor_id=vendor1.id, name="Pro Ultrabook 15-inch Laptop", description="Intel i7 processor, 16GB RAM, 512GB SSD, 15.6-inch Full HD display for productivity and video editing.", price=999.00, stock_quantity=15, category="Electronics", sku="APX-LTP-15"),
            Product(vendor_id=vendor1.id, name="Gaming Laptop Pro 16-inch", description="Intel i9 processor, NVIDIA RTX 4070 GPU, 32GB DDR5 RAM, 1TB NVMe SSD, 240Hz QHD display.", price=1499.00, stock_quantity=8, category="Electronics", sku="APX-LTP-16G"),
            Product(vendor_id=vendor1.id, name="Flagship Smartphone 5G", description="6.7-inch AMOLED display, 256GB storage, 50MP triple camera system, 5000mAh battery.", price=899.00, stock_quantity=25, category="Electronics", sku="APX-PHN-5G"),
            Product(vendor_id=vendor1.id, name="Wireless Noise-Canceling Headphones", description="Active noise cancellation, 30-hour battery life, custom 40mm audio drivers, spatial audio support.", price=299.99, stock_quantity=45, category="Electronics", sku="APX-WHP-01"),
            Product(vendor_id=vendor1.id, name="True Wireless Earbuds Pro", description="Active Noise Cancellation, IPX5 water resistance, wireless charging case, 24-hour total battery.", price=149.00, stock_quantity=60, category="Electronics", sku="APX-EBD-PRO"),
            Product(vendor_id=vendor1.id, name="4K Ultra HD Smart TV", description="55-inch OLED display, HDR10+, Dolby Atmos audio, smart voice control system.", price=649.00, stock_quantity=18, category="Electronics", sku="APX-TV-4K55"),
            Product(vendor_id=vendor1.id, name="65-inch QLED 8K Smart TV", description="Quantum Dot technology, 8K resolution, 120Hz refresh rate, HDMI 2.1 gaming support.", price=1799.00, stock_quantity=5, category="Electronics", sku="APX-TV-8K65"),
            Product(vendor_id=vendor1.id, name="Mechanical Gaming Keyboard", description="Hot-swappable RGB mechanical keyboard with tactile mechanical switches.", price=129.99, stock_quantity=4, category="Electronics", sku="APX-KBD-RGB"),
            Product(vendor_id=vendor1.id, name="Ergonomic Wireless Mouse", description="Precision 16000 DPI optical sensor with dual Bluetooth and USB wireless receiver.", price=49.50, stock_quantity=35, category="Electronics", sku="APX-MSE-04"),
            Product(vendor_id=vendor1.id, name="UltraWide Curved Monitor 34-inch", description="WQHD 3440x1440 resolution, 144Hz refresh rate, 1ms response time, HDR400.", price=499.00, stock_quantity=12, category="Electronics", sku="APX-MON-34UW"),
            Product(vendor_id=vendor1.id, name="Smart Home Hub Display", description="10-inch HD touchscreen, built-in smart assistant, home automation control center.", price=119.00, stock_quantity=20, category="Electronics", sku="APX-HUB-10"),

            # Urban Fashion House (Vendor 2)
            Product(vendor_id=vendor2.id, name="Premium Leather Jacket", description="Handcrafted genuine lambskin leather jacket with silk lining and heavy-duty YKK zippers.", price=189.50, stock_quantity=28, category="Apparel", sku="UFH-LJK-02"),
            Product(vendor_id=vendor2.id, name="Classic Denim Overshirt", description="100% Japanese raw denim, relaxed tailored fit, dual chest pockets.", price=79.00, stock_quantity=40, category="Apparel", sku="UFH-DNM-04"),
            Product(vendor_id=vendor2.id, name="Italian Suede Chelsea Boots", description="Premium suede boots with Goodyear welted leather sole and elastic side goring.", price=220.00, stock_quantity=2, category="Apparel", sku="UFH-BOT-05"),
            Product(vendor_id=vendor2.id, name="Waterproof Trail Running Shoes", description="Vibram high-traction outsole, breathable waterproof membrane, cushioned EVA midsole.", price=135.00, stock_quantity=30, category="Apparel", sku="UFH-SHO-TRL"),
            Product(vendor_id=vendor2.id, name="Organic Cotton Graphic Hoodie", description="Heavyweight 400gsm organic cotton hoodie with fleece lining.", price=65.00, stock_quantity=50, category="Apparel", sku="UFH-HD-08"),
            Product(vendor_id=vendor2.id, name="Tailored Wool Blend Blazer", description="Slim fit Italian wool blend blazer suitable for formal and smart casual wear.", price=245.00, stock_quantity=14, category="Apparel", sku="UFH-BLZ-WL"),
            Product(vendor_id=vendor2.id, name="Minimalist Leather Backpack", description="Top-grain cowhide leather with padded 15-inch laptop compartment.", price=160.00, stock_quantity=18, category="Apparel", sku="UFH-BPK-LTH"),
            Product(vendor_id=vendor2.id, name="Polarized Titanium Sunglasses", description="Lightweight titanium frame with polarized UV400 protective lenses.", price=95.00, stock_quantity=22, category="Apparel", sku="UFH-SUN-TIT"),

            # FitTech Pro Gear (Vendor 3)
            Product(vendor_id=vendor3.id, name="Smart Fitness Tracker Band", description="Continuous heart rate & SpO2 tracking with AMOLED display and 14-day battery.", price=49.99, stock_quantity=6, category="Fitness", sku="FIT-TRK-01"),
            Product(vendor_id=vendor3.id, name="GPS Multisport Smartwatch", description="Built-in GPS, altimeter, offline color mapping, VO2 max estimation, 100m water rating.", price=249.00, stock_quantity=16, category="Fitness", sku="FIT-WCH-GPS"),
            Product(vendor_id=vendor3.id, name="Adjustable Dumbbell Set 24kg", description="Compact dial-select weights ranging from 2.5kg to 24kg for home gym workouts.", price=299.00, stock_quantity=12, category="Fitness", sku="FIT-DBL-24"),
            Product(vendor_id=vendor3.id, name="Non-Slip Yoga Mat Pro", description="6mm eco-friendly natural rubber workout mat with alignment markings.", price=35.00, stock_quantity=0, category="Fitness", sku="FIT-MAT-03"),
            Product(vendor_id=vendor3.id, name="Foldable Treadmill Pro", description="3.0 HP motor, 15% automatic incline, Bluetooth speakers, integrated workout programs.", price=799.00, stock_quantity=7, category="Fitness", sku="FIT-TRD-799"),
            Product(vendor_id=vendor3.id, name="Heavy Duty Resistance Band Set", description="5-level natural latex exercise bands with door anchor and handles.", price=24.99, stock_quantity=50, category="Fitness", sku="FIT-BND-SET"),

            # Luxe Home Essentials (Vendor 4)
            Product(vendor_id=vendor4.id, name="Automatic Espresso Coffee Machine", description="15-bar Italian pump pressure, integrated conical burr grinder, automatic milk frother.", price=449.00, stock_quantity=10, category="Home & Kitchen", sku="LXH-ESP-15B"),
            Product(vendor_id=vendor4.id, name="Robotic Vacuum Cleaner & Mop", description="LiDAR laser navigation, 4000Pa suction power, auto-empty dust dock, app scheduling.", price=399.00, stock_quantity=14, category="Home & Kitchen", sku="LXH-VAC-LID"),
            Product(vendor_id=vendor4.id, name="Air Purifier Pro HEPA H13", description="True HEPA filtration, covers 500 sq ft, real-time air quality indicator, ultra-quiet night mode.", price=179.00, stock_quantity=25, category="Home & Kitchen", sku="LXH-PUR-H13"),
            Product(vendor_id=vendor4.id, name="Stainless Steel Cookware 10-Piece Set", description="Tri-ply stainless steel construction, induction compatible, oven safe up to 260 degrees C.", price=210.00, stock_quantity=15, category="Home & Kitchen", sku="LXH-CW-10P"),

            # Fresh Foods Organic (Pending Approval Vendor)
            Product(vendor_id=vendor_pending.id, name="Cold Pressed Extra Virgin Olive Oil 1L", description="Single-origin organic cold-pressed extra virgin olive oil.", price=22.00, stock_quantity=40, category="Groceries", sku="FFO-OIL-1L"),
            Product(vendor_id=vendor_pending.id, name="Organic Ceremonial Matcha Powder 250g", description="First-harvest ceremonial grade Japanese matcha green tea powder.", price=28.00, stock_quantity=30, category="Groceries", sku="FFO-MTC-250")
        ]

        db.add_all(products)
        db.commit()

        # Build product mapping by SKU for transaction creation
        prod_map = {p.sku: p for p in products}

        print("Seeding 30-Day Multi-Category Transaction Matrix...")
        now = datetime.utcnow()
        tx_specs = [
            # Week 4 ago (Days 25-28)
            (c_vip1.id, vendor1.id, prod_map["APX-LTP-15"].id, 1, prod_map["APX-LTP-15"].price, now - timedelta(days=28)),
            (c_vip2.id, vendor2.id, prod_map["UFH-LJK-02"].id, 1, prod_map["UFH-LJK-02"].price, now - timedelta(days=27)),
            (c_vip3.id, vendor4.id, prod_map["LXH-ESP-15B"].id, 1, prod_map["LXH-ESP-15B"].price, now - timedelta(days=26)),
            (c_reg1.id, vendor1.id, prod_map["APX-PHN-5G"].id, 1, prod_map["APX-PHN-5G"].price, now - timedelta(days=25)),

            # Week 3 ago (Days 18-24)
            (c_vip1.id, vendor1.id, prod_map["APX-WHP-01"].id, 1, prod_map["APX-WHP-01"].price, now - timedelta(days=22)),
            (c_vip3.id, vendor3.id, prod_map["FIT-DBL-24"].id, 1, prod_map["FIT-DBL-24"].price, now - timedelta(days=20)),
            (c_reg2.id, vendor4.id, prod_map["LXH-VAC-LID"].id, 1, prod_map["LXH-VAC-LID"].price, now - timedelta(days=19)),
            (c_vip2.id, vendor2.id, prod_map["UFH-BLZ-WL"].id, 1, prod_map["UFH-BLZ-WL"].price, now - timedelta(days=18)),

            # Week 2 ago (Days 10-17)
            (c_reg1.id, vendor2.id, prod_map["UFH-DNM-04"].id, 2, prod_map["UFH-DNM-04"].price, now - timedelta(days=15)),
            (c_reg2.id, vendor3.id, prod_map["FIT-TRK-01"].id, 1, prod_map["FIT-TRK-01"].price, now - timedelta(days=14)),
            (c_vip2.id, vendor2.id, prod_map["UFH-BOT-05"].id, 1, prod_map["UFH-BOT-05"].price, now - timedelta(days=12)),
            (c_vip1.id, vendor1.id, prod_map["APX-MON-34UW"].id, 1, prod_map["APX-MON-34UW"].price, now - timedelta(days=11)),
            (c_new1.id, vendor4.id, prod_map["LXH-PUR-H13"].id, 1, prod_map["LXH-PUR-H13"].price, now - timedelta(days=10)),

            # Week 1 ago (Days 1-9)
            (c_vip1.id, vendor1.id, prod_map["APX-KBD-RGB"].id, 2, prod_map["APX-KBD-RGB"].price, now - timedelta(days=8)),
            (c_vip3.id, vendor1.id, prod_map["APX-WHP-01"].id, 1, prod_map["APX-WHP-01"].price, now - timedelta(days=7)),
            (c_vip2.id, vendor3.id, prod_map["FIT-WCH-GPS"].id, 1, prod_map["FIT-WCH-GPS"].price, now - timedelta(days=6)),
            (c_new1.id, vendor2.id, prod_map["UFH-HD-08"].id, 1, prod_map["UFH-HD-08"].price, now - timedelta(days=5)),
            (c_new2.id, vendor1.id, prod_map["APX-MSE-04"].id, 2, prod_map["APX-MSE-04"].price, now - timedelta(days=3)),
            (c_reg1.id, vendor3.id, prod_map["FIT-BND-SET"].id, 2, prod_map["FIT-BND-SET"].price, now - timedelta(days=2)),
            (c_vip2.id, vendor2.id, prod_map["UFH-BPK-LTH"].id, 1, prod_map["UFH-BPK-LTH"].price, now - timedelta(days=1))
        ]

        for customer_id, vendor_id, product_id, qty, unit_price, t_date in tx_specs:
            t_obj = Transaction(
                customer_id=customer_id,
                vendor_id=vendor_id,
                product_id=product_id,
                quantity=qty,
                unit_price=unit_price,
                total_amount=qty * unit_price,
                status="completed",
                transaction_date=t_date
            )
            db.add(t_obj)

        db.commit()
        print("Database successfully seeded with accurate prices, 30+ products, customer tiers, and transactions!")
        print("\nSeed Summary:")
        print(f"  Vendors: {db.query(Vendor).count()} (4 Approved, 1 Pending)")
        print(f"  Products: {db.query(Product).count()} across Electronics, Apparel, Fitness, Home & Kitchen, Groceries")
        print(f"  Customers: {db.query(Customer).count()} RFM Segmented Profiles")
        print(f"  Transactions: {db.query(Transaction).count()} Completed 30-Day Orders")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
