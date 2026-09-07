import os
import sys
sys.path.insert(0, os.path.abspath("."))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def run_tests():
    print("=== Testing Milestone 4 Deliverables ===")

    # 1. Admin Auth
    admin_res = client.post("/api/v1/auth/login", json={"email": "admin@shopsense.com", "password": "adminpassword123"})
    assert admin_res.status_code == 200
    cookies = admin_res.cookies
    print("1. Authentication Handshake: OK")

    # 2. AI Copywriter & Listing Generator API
    copy_res = client.post(
        "/api/v1/ai/generate-listing",
        json={
            "raw_notes": "wireless noise-canceling headphones over ear 40h battery",
            "category": "Electronics",
            "target_price": 299.99
        },
        cookies=cookies
    )
    assert copy_res.status_code == 200, f"Copywriter failed: {copy_res.text}"
    c_data = copy_res.json()
    assert "suggested_title" in c_data
    assert "detailed_description" in c_data
    assert len(c_data["seo_tags"]) >= 3
    print(f"2. AI Product Copywriter API: OK (Title: '{c_data['suggested_title']}')")

    # 3. AI Smart Price Optimizer API
    price_res = client.post(
        "/api/v1/ai/price-optimizer",
        json={"product_id": 1},
        cookies=cookies
    )
    assert price_res.status_code == 200, f"Price optimizer failed: {price_res.text}"
    p_data = price_res.json()
    assert "recommended_price" in p_data
    assert "pricing_strategy_rationale" in p_data
    print(f"3. AI Smart Price Optimizer API: OK (Current: INR {p_data['current_price']:.2f} -> Rec: INR {p_data['recommended_price']:.2f})")

    # 4. WebSocket Event Stream Handshake
    with client.websocket_connect("/ws/events") as websocket:
        data = websocket.receive_json()
        assert data["event_type"] == "CONNECTED"
        print("4. Real-Time WebSocket Event Stream Handshake: OK")

    print("\nALL MILESTONE 4 VERIFICATION TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    run_tests()
