"""
Evidence Ingestion, Integrity Verification, Tamper Testing, and Blockchain Anchoring Endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional

from backend.app.core.database import get_db
from backend.app.core.security import get_current_user, require_roles
from backend.app.schemas.case import EvidenceCreate, EvidenceResponse
from backend.app.schemas.custody import EvidenceTamperRequest, BlockchainAnchorRequest
from backend.app.services.evidence_service import EvidenceService
from backend.app.models.case import Evidence, Case
from backend.app.models.custody import CustodyEvent
from blockchain.client import BlockchainAnchorClient
from forensic_engine.custody import create_custody_event, CustodyAction

router = APIRouter(tags=["Evidence & Integrity"])
anchor_client = BlockchainAnchorClient()


@router.post("/cases/{case_id}/evidence")
def ingest_evidence(
    case_id: str,
    evidence_in: EvidenceCreate,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(require_roles(["ADMIN", "INVESTIGATOR"]))
):
    case = db.query(Case).filter(Case.case_id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    ev = EvidenceService.ingest_transaction_evidence(
        db=db,
        case_id=case_id,
        transaction_id=evidence_in.transaction_id,
        source_wallet=evidence_in.source_wallet,
        destination_wallet=evidence_in.destination_wallet,
        amount=evidence_in.amount,
        timestamp=evidence_in.timestamp,
        source=evidence_in.source or "BLOCKCHAIN_INGESTION",
        source_identifier=evidence_in.source_identifier or "NODE_01",
        actor=current_user["username"],
        role=current_user["role"]
    )
    return {
        "status": "SUCCESS",
        "message": f"Evidence {ev.evidence_id} registered and hashed",
        "evidence_id": ev.evidence_id,
        "integrity_digest": ev.integrity_digest,
        "risk_score": ev.risk_score,
        "confidence": ev.confidence,
        "uncertainty_delta": ev.uncertainty_delta,
        "analyst_status": ev.analyst_status,
        "verification": "INTEGRITY_VERIFIED"
    }


@router.get("/cases/{case_id}/evidence")
def list_case_evidence(
    case_id: str,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    items = db.query(Evidence).filter(Evidence.case_id == case_id).offset(skip).limit(limit).all()
    return items


@router.get("/evidence/{evidence_id}")
def get_evidence_detail(
    evidence_id: str,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    ev = db.query(Evidence).filter(Evidence.evidence_id == evidence_id).first()
    if not ev:
        raise HTTPException(status_code=404, detail="Evidence item not found")
    return ev


@router.post("/evidence/{evidence_id}/verify")
def verify_evidence_endpoint(
    evidence_id: str,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    res = EvidenceService.verify_evidence(db, evidence_id)
    if res.get("status") == "NOT_FOUND":
        raise HTTPException(status_code=404, detail="Evidence not found")

    # Record custody audit for verification
    ev = db.query(Evidence).filter(Evidence.evidence_id == evidence_id).first()
    if ev:
        last_evt = db.query(CustodyEvent).filter(CustodyEvent.case_id == ev.case_id).order_by(CustodyEvent.created_at.desc()).first()
        prev_h = last_evt.event_hash if last_evt else None
        evt = create_custody_event(
            case_id=ev.case_id,
            evidence_id=evidence_id,
            actor=current_user["username"],
            role=current_user["role"],
            action=CustodyAction.EVIDENCE_VERIFIED,
            previous_hash=prev_h,
            metadata={"verification_status": res["status"], "is_valid": res["is_valid"]}
        )
        db_evt = CustodyEvent(
            event_id=evt["event_id"],
            case_id=evt["case_id"],
            evidence_id=evt["evidence_id"],
            actor=evt["actor"],
            role=evt["role"],
            action=evt["action"],
            timestamp=evt["timestamp"],
            metadata_json=evt["metadata"],
            previous_hash=evt["previous_hash"],
            event_hash=evt["event_hash"]
        )
        db.add(db_evt)
        db.commit()

    return res


@router.post("/evidence/{evidence_id}/tamper")
def simulate_tamper_endpoint(
    evidence_id: str,
    req: EvidenceTamperRequest,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(require_roles(["ADMIN", "INVESTIGATOR"]))
):
    res = EvidenceService.simulate_tampering(db, evidence_id, req.field_to_modify, req.new_value)
    if "error" in res:
        raise HTTPException(status_code=404, detail=res["error"])
    return res


@router.post("/evidence/{evidence_id}/restore")
def restore_evidence_endpoint(
    evidence_id: str,
    req: EvidenceTamperRequest,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(require_roles(["ADMIN", "INVESTIGATOR"]))
):
    res = EvidenceService.restore_evidence(db, evidence_id, req.field_to_modify, req.new_value)
    if "error" in res:
        raise HTTPException(status_code=404, detail=res["error"])
    return res


@router.post("/evidence/{evidence_id}/anchor")
def anchor_evidence_endpoint(
    evidence_id: str,
    req: BlockchainAnchorRequest,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(require_roles(["ADMIN", "INVESTIGATOR", "ANALYST"]))
):
    ev = db.query(Evidence).filter(Evidence.evidence_id == evidence_id).first()
    if not ev:
        raise HTTPException(status_code=404, detail="Evidence not found")

    try:
        anchor_res = anchor_client.submit_evidence(
            evidence_id=ev.evidence_id,
            digest=ev.integrity_digest,
            submitter=req.submitter or current_user["username"]
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    ev.is_anchored = True
    ev.blockchain_tx_hash = anchor_res["transaction_hash"]
    ev.blockchain_block = anchor_res["block_number"]
    db.commit()
    db.refresh(ev)

    # Log custody event
    last_evt = db.query(CustodyEvent).filter(CustodyEvent.case_id == ev.case_id).order_by(CustodyEvent.created_at.desc()).first()
    prev_h = last_evt.event_hash if last_evt else None
    evt = create_custody_event(
        case_id=ev.case_id,
        evidence_id=evidence_id,
        actor=current_user["username"],
        role=current_user["role"],
        action=CustodyAction.EVIDENCE_ANCHORED,
        previous_hash=prev_h,
        metadata={"tx_hash": ev.blockchain_tx_hash, "block": ev.blockchain_block}
    )
    db_evt = CustodyEvent(
        event_id=evt["event_id"],
        case_id=evt["case_id"],
        evidence_id=evt["evidence_id"],
        actor=evt["actor"],
        role=evt["role"],
        action=evt["action"],
        timestamp=evt["timestamp"],
        metadata_json=evt["metadata"],
        previous_hash=evt["previous_hash"],
        event_hash=evt["event_hash"]
    )
    db.add(db_evt)
    db.commit()

    return {
        "status": "ANCHORED",
        "evidence_id": evidence_id,
        "anchor_details": anchor_res
    }


@router.get("/evidence/{evidence_id}/custody")
def get_evidence_custody(
    evidence_id: str,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    events = db.query(CustodyEvent).filter(CustodyEvent.evidence_id == evidence_id).order_by(CustodyEvent.timestamp).all()
    return events
