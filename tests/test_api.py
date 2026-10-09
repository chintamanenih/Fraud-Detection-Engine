# tests/test_api.py
from fastapi.testclient import TestClient
from src.api.app import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["engine_loaded"] is True

def test_score_transaction():
    payload = {
        "transaction_id": "tx_test_999",
        "user_id": "user_123",
        "amount": 450.75,
        "device_id": "device_xyz",
        "ip_address": "10.0.0.1"
    }
    response = client.post("/v1/score", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["transaction_id"] == "tx_test_999"
    assert "risk_score" in data
    assert "is_anomaly" in data
    assert "collusive_ring_detected" in data
    assert "latency_ms" in data

def test_collusive_ring_detection():
    """Simulates multiple distinct users sharing the exact same device and IP 
    to trigger the advanced NetworkX graph cluster intersection logic."""
    device_shared = "device_syndicate_77"
    ip_shared = "192.168.100.50"

    # User 1 sends a transaction
    client.post("/v1/score", json={
        "transaction_id": "tx_ring_1",
        "user_id": "user_alpha",
        "amount": 50.0,
        "device_id": device_shared,
        "ip_address": ip_shared
    })

    # User 2 sends a transaction using the exact same infrastructure
    client.post("/v1/score", json={
        "transaction_id": "tx_ring_2",
        "user_id": "user_beta",
        "amount": 75.0,
        "device_id": device_shared,
        "ip_address": ip_shared
    })

    # User 3 triggers the cluster threshold intersection
    response = client.post("/v1/score", json={
        "transaction_id": "tx_ring_3",
        "user_id": "user_gamma",
        "amount": 100.0,
        "device_id": device_shared,
        "ip_address": ip_shared
    })

    assert response.status_code == 200
    data = response.json()
    # Verify that the graph engine successfully flagged the multi-user syndicate ring
    assert data["collusive_ring_detected"] is True
    assert data["risk_score"] > 0.4  # Risk score should be elevated due to the ring boost