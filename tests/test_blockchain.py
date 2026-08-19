"""
Unit Tests for Blockchain Smart Contract Evidence Anchoring and Verification.
"""

import pytest
from blockchain.client import BlockchainAnchorClient


def test_blockchain_anchor_submission_and_verification():
    client = BlockchainAnchorClient()

    evidence_id = "ev_blockchain_test_001"
    digest = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"

    # 1. Submit Anchor
    res = client.submit_evidence(evidence_id=evidence_id, digest=digest)
    assert res["status"] == "CONFIRMED_ON_CHAIN"
    assert res["evidence_id"] == evidence_id
    assert res["block_number"] > 0

    # 2. Verify Valid Anchor
    verif = client.verify_evidence(evidence_id=evidence_id, candidate_digest=digest)
    assert verif["is_anchored"] is True
    assert verif["digest_matches"] is True
    assert verif["status"] == "ANCHOR_VERIFIED"

    # 3. Verify Mismatch when Candidate Digest is altered
    tampered_digest = "0000000000000000000000000000000000000000000000000000000000000000"
    verif_tampered = client.verify_evidence(evidence_id=evidence_id, candidate_digest=tampered_digest)
    assert verif_tampered["is_anchored"] is True
    assert verif_tampered["digest_matches"] is False
    assert verif_tampered["status"] == "ANCHOR_DIGEST_MISMATCH"


def test_blockchain_duplicate_prevention():
    client = BlockchainAnchorClient()
    evidence_id = "ev_duplicate_test"
    digest = "aaaa111122223333444455556666777788889999000011112222333344445555"

    client.submit_evidence(evidence_id, digest)

    with pytest.raises(ValueError) as exc_info:
        client.submit_evidence(evidence_id, digest)

    assert "Duplicate Error" in str(exc_info.value)
