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
    """Seed database with realistic multi-vendor products, realistic Indian pricing, customer profiles, and 30-day transactions."""
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
            description="Premium consumer electronics, high-performance laptops, audio gear, and smart appliances.",
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
            description="Modern apparel, luxury leather goods, tailored denim, and designer footwear.",
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
            description="Professional home workout equipment, athletic footwear, and smart health trackers.",
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
            description="Certified organic groceries, cold-pressed oils, and artisanal health foods.",
            role=UserRole.VENDOR,
            approval_status=ApprovalStatus.PENDING,
            is_active=False
        )

        db.add_all([vendor1, vendor2, vendor3, vendor_pending])
        db.commit()

        print("Seeding Customers across RFM segmentation tiers...")
        c1 = Customer(name="Ananya Sharma", email="ananya.sharma@example.com", phone="+91-9811223344", address="702 Prestige Towers, Indiranagar, Bangalore")
        c2 = Customer(name="Rahul Verma", email="rahul.verma@example.com", phone="+91-9822334455", address="14 Palm Grove, Bandra West, Mumbai")
        c3 = Customer(name="Siddharth Malhotra", email="sid.malhotra@example.com", phone="+91-9833112233", address="99 Jubilee Hills, Hyderabad")
        c4 = Customer(name="Priya Patel", email="priya.patel@example.com", phone="+91-9833445566", address="56 Navrangpura, Ahmedabad")
        c5 = Customer(name="Vikram Singh", email="vikram.singh@example.com", phone="+91-9844112233", address="12 Civil Lines, Jaipur")
        c6 = Customer(name="Aditya Kumar", email="aditya.kumar@example.com", phone="+91-9844556677", address="204 DLF Phase 5, Gurgaon")
        c7 = Customer(name="Sneha Reddy", email="sneha.reddy@example.com", phone="+91-9855112233", address="45 Park Street, Kolkata")
        c8 = Customer(name="Kavita Rao", email="kavita.rao@example.com", phone="+91-9855667788", address="88 Anna Nagar, Chennai")
        c9 = Customer(name="Rohan Gupta", email="rohan.gupta@example.com", phone="+91-9866112233", address="33 Koregaon Park, Pune")
        c10 = Customer(name="Meera Joshi", email="meera.joshi@example.com", phone="+91-9877223344", address="102 Vasant Vihar, New Delhi")

        db.add_all([c1, c2, c3, c4, c5, c6, c7, c8, c9, c10])
        db.commit()

        print("Seeding Realistic Catalog Products with Indian Market Prices...")
        # Apex Electronics Products
        p1 = Product(vendor_id=vendor1.id, name="Pro Ultrabook 15-inch Laptop", description="Intel Core i7 13th Gen processor, 16GB LPDDR5 RAM, 512GB NVMe SSD, 15.6-inch Full HD Anti-Glare IPS display laptop for high-productivity business tasks.", price=64999.00, stock_quantity=15, category="Electronics", sku="APX-LTP-15")
        p2 = Product(vendor_id=vendor1.id, name="Flagship Gaming Laptop 16-inch", description="AMD Ryzen 9 7940HS, NVIDIA RTX 4070 8GB VRAM, 32GB DDR5 RAM, 1TB SSD, 240Hz QHD display.", price=119999.00, stock_quantity=8, category="Electronics", sku="APX-LTP-16G")
        p3 = Product(vendor_id=vendor1.id, name="Wireless Noise-Canceling Headphones", description="Industry-leading active noise cancellation, 30-hour playback, dual mic clear calling, spatial audio support.", price=8999.00, stock_quantity=45, category="Electronics", sku="APX-WHP-01")
        p4 = Product(vendor_id=vendor1.id, name="Studio Monitor Headphones", description="Professional closed-back studio reference headphones with 45mm neodymium drivers.", price=14999.00, stock_quantity=20, category="Electronics", sku="APX-WHP-02")
        p5 = Product(vendor_id=vendor1.id, name="4K Ultra HD Smart TV 55-inch", description="55-inch OLED 4K display, HDR10+, Dolby Vision, Dolby Atmos 40W speakers, Google TV OS.", price=44999.00, stock_quantity=18, category="Electronics", sku="APX-TV-4K")
        p6 = Product(vendor_id=vendor1.id, name="Mechanical Gaming Keyboard", description="Hot-swappable tactile switches, per-key RGB backlighting, aircraft-grade aluminum top frame.", price=4999.00, stock_quantity=4, category="Electronics", sku="APX-KBD-RGB")
        p7 = Product(vendor_id=vendor1.id, name="Ergonomic Wireless Mouse", description="High-precision 4000 DPI sensor, silent click switches, dual Bluetooth and 2.4GHz wireless.", price=1899.00, stock_quantity=35, category="Electronics", sku="APX-MSE-04")
        p8 = Product(vendor_id=vendor1.id, name="Smartwatch Pro Series", description="1.43-inch AMOLED display, ECG monitoring, GPS tracking, 7-day battery life, stainless steel case.", price=18999.00, stock_quantity=22, category="Electronics", sku="APX-WCH-PRO")
        p9 = Product(vendor_id=vendor1.id, name="Portable Bluetooth Speaker 20W", description="IP67 waterproof outdoor speaker with deep bass radiator and 15-hour battery.", price=3999.00, stock_quantity=30, category="Electronics", sku="APX-SPK-20W")

        # Urban Fashion House Products
        p10 = Product(vendor_id=vendor2.id, name="Premium Leather Jacket", description="Handcrafted genuine lambskin leather jacket with soft silk interior lining and YKK metal zippers.", price=8999.00, stock_quantity=28, category="Apparel", sku="UFH-LJK-02")
        p11 = Product(vendor_id=vendor2.id, name="Classic Denim Overshirt", description="100% heavy denim cotton overshirt, relaxed tailored fit with double chest pockets.", price=2499.00, stock_quantity=40, category="Apparel", sku="UFH-DNM-04")
        p12 = Product(vendor_id=vendor2.id, name="Italian Suede Chelsea Boots", description="Hand-finished premium suede Chelsea boots with Goodyear welted leather sole.", price=5999.00, stock_quantity=2, category="Apparel", sku="UFH-BOT-05")
        p13 = Product(vendor_id=vendor2.id, name="Organic Cotton Graphic Hoodie", description="Heavyweight 400gsm combed organic cotton fleece hoodie.", price=1999.00, stock_quantity=50, category="Apparel", sku="UFH-HD-08")
        p14 = Product(vendor_id=vendor2.id, name="Designer Leather Handbag", description="Full-grain calfskin leather shoulder bag with gold-plated hardware.", price=6999.00, stock_quantity=12, category="Apparel", sku="UFH-BAG-09")
        p15 = Product(vendor_id=vendor2.id, name="Slim Fit Chino Trousers", description="Stretch cotton twill casual chinos with stain-resistant finish.", price=2299.00, stock_quantity=35, category="Apparel", sku="UFH-CHN-10")

        # FitTech Pro Gear Products
        p16 = Product(vendor_id=vendor3.id, name="Smart Fitness Tracker Band", description="Continuous heart rate, SpO2 monitor, sleep cycle tracking, and 50m water resistance.", price=2999.00, stock_quantity=6, category="Fitness", sku="FIT-TRK-01")
        p17 = Product(vendor_id=vendor3.id, name="Adjustable Dumbbell Set 24kg", description="Dial-selection weight mechanism replacing 15 sets of weights, heavy-duty steel molding.", price=12999.00, stock_quantity=12, category="Fitness", sku="FIT-DBL-24")
        p18 = Product(vendor_id=vendor3.id, name="Non-Slip Yoga Mat Pro", description="6mm eco-friendly natural tree rubber alignment mat with high cushioning.", price=1499.00, stock_quantity=0, category="Fitness", sku="FIT-MAT-03")
        p19 = Product(vendor_id=vendor3.id, name="Running Shoes Cushion Pro", description="Breathable mesh upper with nitrogen-infused midsole responsive cushioning.", price=4499.00, stock_quantity=25, category="Fitness", sku="FIT-SHO-07")
        p20 = Product(vendor_id=vendor3.id, name="Whey Protein Isolate 2kg", description="27g pure whey protein isolate per serving with digestive enzyme blend.", price=4999.00, stock_quantity=40, category="Fitness", sku="FIT-NUT-09")

        # Fresh Foods Organic Products
        p21 = Product(vendor_id=vendor_pending.id, name="Cold Pressed Extra Virgin Olive Oil 1L", description="Single-origin cold-pressed extra virgin olive oil.", price=1299.00, stock_quantity=50, category="Groceries", sku="FFO-OIL-01")
        p22 = Product(vendor_id=vendor_pending.id, name="Raw Wildflower Honey 500g", description="Unfiltered raw organic honey harvested from wild forest reserves.", price=599.00, stock_quantity=60, category="Groceries", sku="FFO-HNY-02")

        db.add_all([p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11, p12, p13, p14, p15, p16, p17, p18, p19, p20, p21, p22])
        db.commit()

        print("Seeding 30-Day Time-Stamped Transaction Matrix...")
        now = datetime.utcnow()
        tx_data = [
            # Week 4 (Days -28 to -21)
            (c1.id, vendor1.id, p1.id, 1, 64999.00, now - timedelta(days=28)),
            (c2.id, vendor2.id, p10.id, 1, 8999.00, now - timedelta(days=27)),
            (c3.id, vendor1.id, p2.id, 1, 119999.00, now - timedelta(days=25)),
            (c4.id, vendor3.id, p17.id, 1, 12999.00, now - timedelta(days=23)),
            (c1.id, vendor1.id, p3.id, 1, 8999.00, now - timedelta(days=22)),

            # Week 3 (Days -20 to -14)
            (c5.id, vendor2.id, p11.id, 2, 2499.00, now - timedelta(days=20)),
            (c6.id, vendor3.id, p16.id, 1, 2999.00, now - timedelta(days=19)),
            (c2.id, vendor2.id, p12.id, 1, 5999.00, now - timedelta(days=17)),
            (c7.id, vendor1.id, p5.id, 1, 44999.00, now - timedelta(days=15)),
            (c8.id, vendor3.id, p19.id, 1, 4499.00, now - timedelta(days=14)),

            # Week 2 (Days -13 to -7)
            (c1.id, vendor1.id, p6.id, 1, 4999.00, now - timedelta(days=12)),
            (c3.id, vendor1.id, p3.id, 1, 8999.00, now - timedelta(days=10)),
            (c9.id, vendor2.id, p13.id, 2, 1999.00, now - timedelta(days=9)),
            (c10.id, vendor2.id, p14.id, 1, 6999.00, now - timedelta(days=8)),
            (c4.id, vendor3.id, p20.id, 2, 4999.00, now - timedelta(days=7)),

            # Week 1 (Days -6 to Present)
            (c6.id, vendor1.id, p7.id, 1, 1899.00, now - timedelta(days=5)),
            (c2.id, vendor1.id, p8.id, 1, 18999.00, now - timedelta(days=4)),
            (c5.id, vendor3.id, p16.id, 1, 2999.00, now - timedelta(days=3)),
            (c7.id, vendor2.id, p15.id, 2, 2299.00, now - timedelta(days=2)),
            (c1.id, vendor1.id, p9.id, 1, 3999.00, now - timedelta(days=1))
        ]

        for customer_id, vendor_id, product_id, quantity, unit_price, transaction_date in tx_data:
            t_obj = Transaction(
                customer_id=customer_id,
                vendor_id=vendor_id,
                product_id=product_id,
                quantity=quantity,
                unit_price=unit_price,
                total_amount=quantity * unit_price,
                status="completed",
                transaction_date=transaction_date
            )
            db.add(t_obj)

        db.commit()
        print("Database successfully seeded with realistic Indian pricing, catalog items, customers, and transactions!")
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
