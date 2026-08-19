"""
Unit Tests for Digital Chain of Custody (Chained Event Ledger).
"""

import pytest
from forensic_engine.custody import create_custody_event, verify_custody_chain, GENESIS_PREV_HASH, CustodyAction


def test_valid_custody_chain_progression():
    case_id = "case_custody_test"
    events = []

    # Event 1: Case Created
    evt1 = create_custody_event(
        case_id=case_id,
        actor="Alice",
        role="INVESTIGATOR",
        action=CustodyAction.CASE_CREATED,
        previous_hash=GENESIS_PREV_HASH
    )
    events.append(evt1)

    # Event 2: Evidence Acquired
    evt2 = create_custody_event(
        case_id=case_id,
        evidence_id="ev_001",
        actor="Alice",
        role="INVESTIGATOR",
        action=CustodyAction.EVIDENCE_ACQUIRED,
        previous_hash=evt1["event_hash"]
    )
    events.append(evt2)

    # Event 3: Model Analyzed
    evt3 = create_custody_event(
        case_id=case_id,
        evidence_id="ev_001",
        actor="AI_Engine",
        role="SYSTEM",
        action=CustodyAction.MODEL_EXECUTED,
        previous_hash=evt2["event_hash"]
    )
    events.append(evt3)

    is_valid, report = verify_custody_chain(events)
    assert is_valid is True
    assert report["total_events"] == 3
    assert len(report["errors"]) == 0


def test_tamper_detection_in_custody_event_payload():
    case_id = "case_custody_tamper"
    evt1 = create_custody_event(case_id=case_id, actor="Alice", role="INVESTIGATOR", action=CustodyAction.CASE_CREATED)
    evt2 = create_custody_event(case_id=case_id, actor="Bob", role="ANALYST", action=CustodyAction.EVIDENCE_VIEWED, previous_hash=evt1["event_hash"])

    chain = [evt1, dict(evt2)]

    # Tamper with actor in event 2 without updating hash
    chain[1]["actor"] = "Attacker"

    is_valid, report = verify_custody_chain(chain)
    assert is_valid is False
    assert report["status"] == "CHAIN_TAMPER_DETECTED"
    assert len(report["errors"]) > 0
    assert report["errors"][0]["error"] == "EVENT_PAYLOAD_TAMPERED"


def test_broken_hash_linkage_detection():
    case_id = "case_custody_broken_link"
    evt1 = create_custody_event(case_id=case_id, actor="Alice", role="INVESTIGATOR", action=CustodyAction.CASE_CREATED)
    evt2 = create_custody_event(case_id=case_id, actor="Bob", role="ANALYST", action=CustodyAction.EVIDENCE_VIEWED, previous_hash="bad_previous_hash_000000000000000000000000000000000000000000000000")

    chain = [evt1, evt2]
    is_valid, report = verify_custody_chain(chain)
    assert is_valid is False
    assert report["errors"][0]["error"] == "CHAIN_LINK_BROKEN"
