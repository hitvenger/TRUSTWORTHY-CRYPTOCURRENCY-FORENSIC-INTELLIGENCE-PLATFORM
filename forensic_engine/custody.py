"""
Digital Chain of Custody (CoC) Ledger for TCF-FX.

Maintains a cryptographically verifiable chained hash audit trail for all evidence actions.
Any modification to an event payload or link in the chain breaks subsequent hashes.
"""

import hashlib
import uuid
import datetime
from typing import List, Dict, Any, Tuple, Optional
from forensic_engine.canonical import canonical_json_bytes, canonical_json_dumps

GENESIS_PREV_HASH = "0000000000000000000000000000000000000000000000000000000000000000"


class CustodyAction:
    EVIDENCE_ACQUIRED = "evidence_acquired"
    EVIDENCE_REGISTERED = "evidence_registered"
    EVIDENCE_VIEWED = "evidence_viewed"
    EVIDENCE_PROCESSED = "evidence_processed"
    EVIDENCE_ANALYZED = "evidence_analyzed"
    MODEL_EXECUTED = "model_executed"
    EXPLANATION_GENERATED = "explanation_generated"
    EVIDENCE_EXPORTED = "evidence_exported"
    EVIDENCE_VERIFIED = "evidence_verified"
    ANALYST_DECISION = "analyst_decision"
    EVIDENCE_ANCHORED = "evidence_anchored"
    REPORT_GENERATED = "report_generated"
    CASE_CREATED = "case_created"
    CASE_STATUS_CHANGED = "case_status_changed"


def compute_event_hash(
    event_id: str,
    case_id: str,
    evidence_id: Optional[str],
    actor: str,
    role: str,
    action: str,
    timestamp: str,
    metadata: Dict[str, Any],
    previous_hash: str
) -> str:
    """Computes SHA-256 hash for a custody event over canonical JSON representation."""
    payload = {
        "event_id": str(event_id),
        "case_id": str(case_id),
        "evidence_id": str(evidence_id) if evidence_id else None,
        "actor": str(actor),
        "role": str(role),
        "action": str(action),
        "timestamp": str(timestamp),
        "metadata": metadata or {},
        "previous_hash": str(previous_hash),
    }
    raw = canonical_json_bytes(payload)
    return hashlib.sha256(raw).hexdigest()


def create_custody_event(
    case_id: str,
    actor: str,
    role: str,
    action: str,
    evidence_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    previous_hash: Optional[str] = None,
    timestamp: Optional[str] = None,
    event_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Creates a new verifiable custody event record."""
    event_id = event_id or f"evt_{uuid.uuid4().hex[:12]}"
    timestamp = timestamp or datetime.datetime.now(datetime.timezone.utc).isoformat()
    metadata = metadata or {}
    prev_hash = previous_hash or GENESIS_PREV_HASH
    
    event_hash = compute_event_hash(
        event_id=event_id,
        case_id=case_id,
        evidence_id=evidence_id,
        actor=actor,
        role=role,
        action=action,
        timestamp=timestamp,
        metadata=metadata,
        previous_hash=prev_hash
    )
    
    return {
        "event_id": event_id,
        "case_id": case_id,
        "evidence_id": evidence_id,
        "actor": actor,
        "role": role,
        "action": action,
        "timestamp": timestamp,
        "metadata": metadata,
        "previous_hash": prev_hash,
        "event_hash": event_hash,
    }


def verify_custody_chain(events: List[Dict[str, Any]]) -> Tuple[bool, Dict[str, Any]]:
    """
    Validates the entire custody event chain.
    Checks:
    1. Genesis previous_hash integrity
    2. Consecutive hash linking (event[i].previous_hash == event[i-1].event_hash)
    3. Self-consistency of every event's event_hash
    """
    if not events:
        return True, {"status": "EMPTY_CHAIN", "total_events": 0, "errors": []}
    
    errors = []
    expected_prev = GENESIS_PREV_HASH
    
    for idx, evt in enumerate(events):
        evt_id = evt.get("event_id", f"idx_{idx}")
        prev_hash = evt.get("previous_hash", "")
        recorded_hash = evt.get("event_hash", "")
        
        # Check linkage
        if prev_hash != expected_prev:
            errors.append({
                "index": idx,
                "event_id": evt_id,
                "error": "CHAIN_LINK_BROKEN",
                "expected_previous_hash": expected_prev,
                "actual_previous_hash": prev_hash,
            })
            
        # Recompute hash
        recomputed = compute_event_hash(
            event_id=evt.get("event_id"),
            case_id=evt.get("case_id"),
            evidence_id=evt.get("evidence_id"),
            actor=evt.get("actor"),
            role=evt.get("role"),
            action=evt.get("action"),
            timestamp=evt.get("timestamp"),
            metadata=evt.get("metadata", {}),
            previous_hash=prev_hash
        )
        
        if recomputed != recorded_hash:
            errors.append({
                "index": idx,
                "event_id": evt_id,
                "error": "EVENT_PAYLOAD_TAMPERED",
                "recorded_hash": recorded_hash,
                "recomputed_hash": recomputed,
            })
            
        # Move forward
        expected_prev = recorded_hash
        
    is_valid = len(errors) == 0
    return is_valid, {
        "status": "CHAIN_INTEGRITY_VERIFIED" if is_valid else "CHAIN_TAMPER_DETECTED",
        "total_events": len(events),
        "is_valid": is_valid,
        "errors": errors,
    }
