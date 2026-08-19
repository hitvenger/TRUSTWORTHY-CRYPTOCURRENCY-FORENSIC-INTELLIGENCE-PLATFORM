"""
Integration Tests for FastAPI Backend Endpoints and RBAC Authorization.
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_health_check_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "HEALTHY"
    assert "Evidence Trust" in data["trust_dimensions"]


def test_auth_login_and_token_generation():
    # Login as lead investigator
    response = client.post("/api/v1/auth/login", json={
        "username": "investigator",
        "password": "investigator123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["role"] == "INVESTIGATOR"


def test_case_creation_and_listing():
    # Create Case
    create_res = client.post("/api/v1/cases", json={
        "title": "API Test Case - Operation Alpha",
        "description": "Integration testing case",
        "investigator": "Agent Fox Mulder",
        "priority": "HIGH",
        "tags": ["TEST", "ETHEREUM"]
    })
    assert create_res.status_code == 201
    case_data = create_res.json()["case"]
    case_id = case_data["case_id"]

    # Fetch Case
    get_res = client.get(f"/api/v1/cases/{case_id}")
    assert get_res.status_code == 200
    assert get_res.json()["title"] == "API Test Case - Operation Alpha"

    # List Cases
    list_res = client.get("/api/v1/cases")
    assert list_res.status_code == 200
    assert len(list_res.json()) > 0


def test_evidence_ingestion_and_tamper_endpoints():
    # 1. Create a case
    c_res = client.post("/api/v1/cases", json={"title": "Tamper Test Case"})
    case_id = c_res.json()["case"]["case_id"]

    # 2. Ingest evidence
    ev_res = client.post(f"/api/v1/cases/{case_id}/evidence", json={
        "case_id": case_id,
        "transaction_id": "tx_api_test_01",
        "source_wallet": "0x_src_api_wallet",
        "destination_wallet": "0x_dst_api_wallet",
        "amount": 35.0,
        "timestamp": 1704067500.0
    })
    assert ev_res.status_code == 200
    ev_data = ev_res.json()
    evidence_id = ev_data["evidence_id"]
    orig_digest = ev_data["integrity_digest"]

    # 3. Verify original
    v_res = client.post(f"/api/v1/evidence/{evidence_id}/verify")
    assert v_res.status_code == 200
    assert v_res.json()["is_valid"] is True

    # 4. Simulate tamper
    t_res = client.post(f"/api/v1/evidence/{evidence_id}/tamper", json={
        "field_to_modify": "amount",
        "new_value": 9999.0
    })
    assert t_res.status_code == 200
    assert t_res.json()["verification_result"]["is_valid"] is False
    assert t_res.json()["verification_result"]["status"] == "TAMPER_DETECTED"

    # 5. Restore
    r_res = client.post(f"/api/v1/evidence/{evidence_id}/restore", json={
        "field_to_modify": "amount",
        "new_value": 35.0
    })
    assert r_res.status_code == 200
    assert r_res.json()["verification_result"]["is_valid"] is True
