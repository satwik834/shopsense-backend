import sys
import os

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from app.main import app

def run_tests():
    client = TestClient(app)
    print("=== Testing Milestone 2 Deliverables ===")

    # 1. Admin Authentication
    admin_login = client.post('/api/v1/auth/login', json={'email': 'admin@shopsense.com', 'password': 'adminpassword123'})
    assert admin_login.status_code == 200, f"Admin login failed: {admin_login.text}"
    admin_client = TestClient(app)
    admin_client.cookies = admin_login.cookies
    print("1. Admin Authentication: OK")

    # 2. Vendor Authentication
    vendor_login = client.post('/api/v1/auth/login', json={'email': 'contact@apex.com', 'password': 'vendorpass123'})
    assert vendor_login.status_code == 200, f"Vendor login failed: {vendor_login.text}"
    vendor_client = TestClient(app)
    vendor_client.cookies = vendor_login.cookies
    print("2. Vendor Authentication: OK")

    # 3. Inventory Stock Levels & Tracking
    stock_res = admin_client.get('/api/v1/inventory/stock-levels?threshold=10')
    assert stock_res.status_code == 200, f"Stock levels failed: {stock_res.text}"
    stock_data = stock_res.json()
    assert stock_data["total_products_tracked"] >= 5
    print(f"3. Inventory Stock Levels: OK (Tracked: {stock_data['total_products_tracked']}, Low Stock: {stock_data['low_stock_count']})")

    # 4. Low-Stock Alerts
    alerts_res = admin_client.get('/api/v1/inventory/low-stock-alerts?threshold=10')
    assert alerts_res.status_code == 200, f"Low-stock alerts failed: {alerts_res.text}"
    alerts = alerts_res.json()
    assert len(alerts) >= 1
    print(f"4. Low-Stock Alerts: OK (Triggered Alerts: {len(alerts)})")

    # 5. Product Restocking API
    test_prod_id = alerts[0]["product_id"]
    old_stock = alerts[0]["current_stock"]
    restock_res = admin_client.put(f'/api/v1/inventory/{test_prod_id}/restock', json={'additional_quantity': 30})
    assert restock_res.status_code == 200, f"Restock failed: {restock_res.text}"
    new_stock = restock_res.json()["stock_quantity"]
    assert new_stock == old_stock + 30
    print(f"5. Inventory Restock API: OK (Product ID {test_prod_id}: {old_stock} -> {new_stock} units)")

    # 6. Demand Run-Rate Forecasting
    forecast_res = admin_client.get(f'/api/v1/inventory/{test_prod_id}/forecast?days=30')
    assert forecast_res.status_code == 200, f"Forecast failed: {forecast_res.text}"
    forecast = forecast_res.json()
    assert "projected_demand" in forecast
    assert "reorder_urgency" in forecast
    print(f"6. Demand Velocity & Forecasting: OK (30-day Demand: {forecast['projected_demand']}, Urgency: {forecast['reorder_urgency']})")

    # 7. Customer Segmentation Overview
    seg_res = admin_client.get('/api/v1/customer-analytics/segments')
    assert seg_res.status_code == 200, f"Segmentation failed: {seg_res.text}"
    seg_data = seg_res.json()
    assert len(seg_data["segments"]) == 4
    print(f"7. SQL-based Customer Segmentation: OK (Total Revenue: {seg_data['total_customer_revenue']})")

    # 8. Filtered Customers List
    vip_res = admin_client.get('/api/v1/customer-analytics/customers?segment=VIP')
    assert vip_res.status_code == 200, f"VIP filter failed: {vip_res.text}"
    vip_custs = vip_res.json()
    assert len(vip_custs) >= 1
    print(f"8. Customer Spend Profiles: OK (VIP Count: {len(vip_custs)})")

    # 9. Top-Selling Category Recommendations
    top_rec = admin_client.get('/api/v1/recommendations/top-selling?category=Electronics')
    assert top_rec.status_code == 200, f"Top selling recs failed: {top_rec.text}"
    assert len(top_rec.json()["top_sellers"]) >= 1
    print(f"9. Category Top-Sellers: OK (Items: {len(top_rec.json()['top_sellers'])})")

    # 10. Frequently Bought Together Cross-Sell
    cross_rec = admin_client.get(f'/api/v1/recommendations/frequently-bought-together/{test_prod_id}')
    assert cross_rec.status_code == 200, f"Cross-sell recs failed: {cross_rec.text}"
    print(f"10. Cross-Sell Recommendations: OK (Pairings: {len(cross_rec.json()['frequently_bought_together'])})")

    # 11. Customer Personalized Recommendations
    cust_rec = admin_client.get('/api/v1/recommendations/customer/1')
    assert cust_rec.status_code == 200, f"Personalized recs failed: {cust_rec.text}"
    print(f"11. Customer Personalized Feed: OK (Recommendations: {len(cust_rec.json()['recommended_products'])})")

    print("\nALL 11 MILESTONE 2 VERIFICATION TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    run_tests()
