"""
Security, Access Control, and Injection Prevention Tests for TCF-FX.
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.core.security import create_access_token
from forensic_engine.canonical import canonical_json_dumps

client = TestClient(app)


def test_rbac_authorization_rejection():
    # Viewer token should be rejected when trying to ingest evidence
    viewer_token = create_access_token({"sub": "viewer_user", "role": "VIEWER", "user_id": "usr_v"})
    headers = {"Authorization": f"Bearer {viewer_token}"}

    res = client.post("/api/v1/cases/case_001/evidence", json={
        "case_id": "case_001",
        "transaction_id": "tx_unauth",
        "source_wallet": "0x_a",
        "destination_wallet": "0x_b",
        "amount": 1.0,
        "timestamp": 1000.0
    }, headers=headers)

    # Must be forbidden (403)
    assert res.status_code == 403
    assert "Access forbidden" in res.json()["detail"]


def test_sql_injection_resilience_in_case_creation():
    # Attempt SQL injection payload in case title
    sqli_title = "Case Alpha'; DROP TABLE cases; --"
    res = client.post("/api/v1/cases", json={
        "title": sqli_title,
        "description": "SQLi injection test description",
        "priority": "HIGH"
    })
    assert res.status_code == 201
    created_case = res.json()["case"]
    assert created_case["title"] == sqli_title

    # Verify table was not dropped and case exists
    get_res = client.get(f"/api/v1/cases/{created_case['case_id']}")
    assert get_res.status_code == 200
    assert get_res.json()["title"] == sqli_title


def test_xss_payload_safety_in_json_and_manifest():
    xss_payload = "<script>alert('XSS_FORENSIC_INJECTION')</script>"
    res = client.post("/api/v1/cases", json={
        "title": xss_payload,
        "description": "XSS safety test"
    })
    assert res.status_code == 201
    case_id = res.json()["case"]["case_id"]

    # Manifest should safely serialize as JSON string
    manifest_res = client.get(f"/api/v1/reports/{case_id}/manifest")
    assert manifest_res.status_code == 200
    assert manifest_res.json()["case_metadata"]["title"] == xss_payload


def test_canonical_json_anti_injection():
    # Nested tricky keys and quotes
    tricky_dict = {
        "key\"with\"quotes": "value",
        "nested": {"deep\\slash": "ok"}
    }
    canonical_str = canonical_json_dumps(tricky_dict)
    assert "\\\"with\\\"quotes" in canonical_str
