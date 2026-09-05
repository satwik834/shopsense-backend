import os
import sys
sys.path.insert(0, os.path.abspath("."))

from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal
from app.models.vendor import Vendor
from app.models.product import Product
from app.models.customer import Customer
from app.models.transaction import Transaction

client = TestClient(app)

def run_tests():
    print("=== Testing Milestone 3 Deliverables ===")

    # 1. Auth Login (Admin & Vendor)
    admin_res = client.post("/api/v1/auth/login", json={"email": "admin@shopsense.com", "password": "adminpassword123"})
    assert admin_res.status_code == 200, f"Admin login failed: {admin_res.text}"
    admin_cookies = admin_res.cookies
    print("1. Admin Authentication: OK")

    vendor_res = client.post("/api/v1/auth/login", json={"email": "contact@apex.com", "password": "vendorpass123"})
    assert vendor_res.status_code == 200, f"Vendor login failed: {vendor_res.text}"
    vendor_cookies = vendor_res.cookies
    print("2. Vendor Authentication: OK")

    # 3. BI Chart: Sales Trends
    trends_res = client.get("/api/v1/bi/charts/sales-trends?days=30", cookies=admin_cookies)
    assert trends_res.status_code == 200, f"Sales trends failed: {trends_res.text}"
    t_data = trends_res.json()
    assert "trend_points" in t_data
    assert len(t_data["trend_points"]) >= 7
    print(f"3. BI Sales Trends Chart API: OK (Revenue: INR {t_data['total_revenue']:.2f}, Orders: {t_data['total_orders']})")

    # 4. BI Chart: Category Distribution
    cat_res = client.get("/api/v1/bi/charts/category-distribution", cookies=admin_cookies)
    assert cat_res.status_code == 200, f"Category distribution failed: {cat_res.text}"
    c_data = cat_res.json()
    assert "categories" in c_data
    assert c_data["total_categories"] >= 1
    print(f"4. BI Category Distribution Chart API: OK (Categories: {c_data['total_categories']})")

    # 5. Vendor Benchmarking
    bench_res = client.get("/api/v1/bi/benchmarking", cookies=vendor_cookies)
    assert bench_res.status_code == 200, f"Vendor benchmarking failed: {bench_res.text}"
    b_data = bench_res.json()
    assert "metrics" in b_data
    assert len(b_data["metrics"]) == 4
    print(f"5. Vendor Performance Benchmarking API: OK (Overall Rating: {b_data['overall_performance_rating']})")

    # 6. CSV Export: Sales
    sales_csv_res = client.get("/api/v1/bi/export/sales-csv", cookies=admin_cookies)
    assert sales_csv_res.status_code == 200
    assert "Transaction ID" in sales_csv_res.text
    print("6. Sales CSV Data Export Stream: OK")

    # 7. CSV Export: Inventory
    inv_csv_res = client.get("/api/v1/bi/export/inventory-csv", cookies=admin_cookies)
    assert inv_csv_res.status_code == 200
    assert "Product ID" in inv_csv_res.text
    print("7. Warehouse Inventory CSV Data Export Stream: OK")

    # 8. CSV Export: Customers
    cust_csv_res = client.get("/api/v1/bi/export/customers-csv", cookies=admin_cookies)
    assert cust_csv_res.status_code == 200
    assert "Customer ID" in cust_csv_res.text
    print("8. Customer RFM Profiles CSV Data Export Stream: OK")

    # 9. AI Shopping Assistant (RAG Search)
    ai_shop_res = client.post(
        "/api/v1/ai/shopping-assistant",
        json={"query": "Find noise canceling headphones under 300", "max_price": 350.0},
        cookies=admin_cookies
    )
    assert ai_shop_res.status_code == 200, f"AI Shopping Assistant failed: {ai_shop_res.text}"
    ai_s_data = ai_shop_res.json()
    assert "suggested_products" in ai_s_data
    assert len(ai_s_data["suggested_products"]) >= 1
    print(f"9. RAG AI Shopping Assistant API: OK (Suggested Matches: {len(ai_s_data['suggested_products'])})")

    # 10. AI Store Advisor
    ai_adv_res = client.post("/api/v1/ai/store-advisor", json={}, cookies=vendor_cookies)
    assert ai_adv_res.status_code == 200, f"AI Store Advisor failed: {ai_adv_res.text}"
    ai_a_data = ai_adv_res.json()
    assert "diagnostics" in ai_a_data
    assert "ai_generated_strategy" in ai_a_data
    print(f"10. AI Store Advisor Audit API: OK (Diagnostics Count: {len(ai_a_data['diagnostics'])})")

    print("\nALL MILESTONE 3 VERIFICATION TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    run_tests()
