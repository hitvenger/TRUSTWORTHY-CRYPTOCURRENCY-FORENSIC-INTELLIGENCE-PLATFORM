"""
End-to-End Forensic Investigation Lifecycle Test for TCF-FX.
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_complete_end_to_end_forensic_lifecycle():
    # 1. Create Case
    c_res = client.post("/api/v1/cases", json={
        "title": "E2E Lifecycle Case - Operation DarkPool",
        "description": "Full end-to-end integration test case",
        "investigator": "Forensic Inspector Sherlock",
        "priority": "CRITICAL",
        "tags": ["E2E", "BITCOIN", "MIXER"]
    })
    assert c_res.status_code == 201
    case_id = c_res.json()["case"]["case_id"]

    # 2. Ingest Evidence
    ev_res = client.post(f"/api/v1/cases/{case_id}/evidence", json={
        "case_id": case_id,
        "transaction_id": "tx_e2e_001",
        "source_wallet": "0x_e2e_source_wallet",
        "destination_wallet": "0x_e2e_dest_wallet",
        "amount": 75.25,
        "timestamp": 1704068000.0,
        "source": "BITCOIN_CORE_NODE",
        "source_identifier": "BLOCK_824105"
    })
    assert ev_res.status_code == 200
    ev_data = ev_res.json()
    evidence_id = ev_data["evidence_id"]
    orig_digest = ev_data["integrity_digest"]
    assert len(orig_digest) == 64

    # 3. Verify Original Integrity
    v1_res = client.post(f"/api/v1/evidence/{evidence_id}/verify")
    assert v1_res.status_code == 200
    assert v1_res.json()["is_valid"] is True
    assert v1_res.json()["status"] == "INTEGRITY_VERIFIED"

    # 4. Fetch SHAP Explanations
    expl_res = client.get(f"/api/v1/transactions/tx_e2e_001/explanation")
    assert expl_res.status_code == 200
    assert "explanation" in expl_res.json()
    assert "top_positive_contributors" in expl_res.json()["explanation"]

    # 5. Simulate Tampering
    t_res = client.post(f"/api/v1/evidence/{evidence_id}/tamper", json={
        "field_to_modify": "amount",
        "new_value": 999999.0
    })
    assert t_res.status_code == 200
    assert t_res.json()["verification_result"]["is_valid"] is False
    assert t_res.json()["verification_result"]["status"] == "TAMPER_DETECTED"

    # 6. Restore Original Integrity
    r_res = client.post(f"/api/v1/evidence/{evidence_id}/restore", json={
        "field_to_modify": "amount",
        "new_value": 75.25
    })
    assert r_res.status_code == 200
    assert r_res.json()["verification_result"]["is_valid"] is True

    # 7. Anchor to Blockchain Smart Contract
    anchor_res = client.post(f"/api/v1/evidence/{evidence_id}/anchor", json={
        "evidence_id": evidence_id,
        "submitter": "0x71C8A...ForensicLead"
    })
    assert anchor_res.status_code == 200
    assert anchor_res.json()["status"] == "ANCHORED"

    # 8. Human Analyst Review: Promote lead to FORENSIC_FINDING
    review_res = client.post("/api/v1/analyst-review", json={
        "case_id": case_id,
        "evidence_id": evidence_id,
        "new_state": "FORENSIC_FINDING",
        "finding_summary": "Confirmed illicit mixer entry transaction with high velocity burst.",
        "rationale": "Analyst reviewed graph topology and SHAP positive contributors, confirming multi-signal alignment.",
        "corroborating_notes": "Corroborated by independent Isolation Forest anomaly score."
    })
    assert review_res.status_code == 200
    assert review_res.json()["new_state"] == "FORENSIC_FINDING"

    # 9. Verify Digital Chain of Custody
    coc_res = client.get(f"/api/v1/audit/custody-chain/{case_id}")
    assert coc_res.status_code == 200
    assert coc_res.json()["is_chain_valid"] is True
    assert coc_res.json()["total_events"] >= 3

    # 10. Generate Reports (PDF, JSON, CSV)
    pdf_res = client.get(f"/api/v1/reports/{case_id}/pdf")
    assert pdf_res.status_code == 200
    assert len(pdf_res.content) > 0

    json_res = client.get(f"/api/v1/reports/{case_id}/manifest")
    assert json_res.status_code == 200
    assert "evidence_inventory" in json_res.json()

    csv_res = client.get(f"/api/v1/reports/{case_id}/csv")
    assert csv_res.status_code == 200
    assert "evidence_id,transaction_id" in csv_res.text
