"""
Unit Tests for SHA-256 Hashing, Tamper Detection, and Field Mutation.
"""

import pytest
from forensic_engine.hashing import create_digest, verify_digest, detect_tampering


@pytest.fixture
def base_evidence_record():
    return {
        "evidence_id": "ev_test_12345",
        "case_id": "case_alpha",
        "transaction_id": "tx_009988",
        "source_wallet": "0x_src_wallet_aaa",
        "destination_wallet": "0x_dst_wallet_bbb",
        "amount": 25.50000000,
        "event_timestamp": "1704067200.0",
        "model_id": "model_rf_baseline",
        "model_version": "1.0.0",
        "risk_score": 0.8540,
        "explanation": "High velocity transfer",
    }


def test_sha256_digest_creation_and_verification(base_evidence_record):
    digest = create_digest(base_evidence_record)
    assert isinstance(digest, str)
    assert len(digest) == 64

    # Verify original record passes
    is_valid, computed, meta = verify_digest(base_evidence_record, expected_digest=digest)
    assert is_valid is True
    assert meta["status"] == "VERIFIED"


@pytest.mark.parametrize("altered_field, mutated_value", [
    ("amount", 25.50000001),
    ("amount", 999.0),
    ("risk_score", 0.12),
    ("event_timestamp", "1704067201.0"),
    ("source_wallet", "0x_src_wallet_tampered"),
    ("destination_wallet", "0x_dst_wallet_tampered"),
    ("model_version", "2.0.0"),
    ("explanation", "Altered benign explanation"),
])
def test_tamper_detection_across_fields(base_evidence_record, altered_field, mutated_value):
    orig_digest = create_digest(base_evidence_record)
    
    # Create tampered copy
    tampered_record = dict(base_evidence_record)
    tampered_record[altered_field] = mutated_value

    # Verify fails
    is_valid, computed, meta = verify_digest(tampered_record, expected_digest=orig_digest)
    assert is_valid is False
    assert meta["status"] == "TAMPER_DETECTED"
    assert computed != orig_digest

    # Detailed tamper analysis
    diff_report = detect_tampering(base_evidence_record, tampered_record)
    assert diff_report["is_tampered"] is True
    assert diff_report["altered_field_count"] == 1
    assert diff_report["altered_fields"][0]["field"] == altered_field
