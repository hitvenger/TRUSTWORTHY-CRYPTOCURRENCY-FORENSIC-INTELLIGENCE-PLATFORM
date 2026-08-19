"""
Digital Chain of Custody & Security Audit Log API Endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional

from backend.app.core.database import get_db
from backend.app.core.security import get_current_user, require_roles
from backend.app.models.custody import CustodyEvent
from forensic_engine.custody import verify_custody_chain

router = APIRouter(prefix="/audit", tags=["Audit Trail & Custody"])


@router.get("/custody-chain/{case_id}")
def get_case_custody_chain(
    case_id: str,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    events = db.query(CustodyEvent).filter(CustodyEvent.case_id == case_id).order_by(CustodyEvent.timestamp).all()
    events_dicts = [
        {
            "event_id": e.event_id,
            "case_id": e.case_id,
            "evidence_id": e.evidence_id,
            "actor": e.actor,
            "role": e.role,
            "action": e.action,
            "timestamp": e.timestamp,
            "metadata": e.metadata_json or {},
            "previous_hash": e.previous_hash,
            "event_hash": e.event_hash
        }
        for e in events
    ]
    is_valid, validation_report = verify_custody_chain(events_dicts)
    
    return {
        "case_id": case_id,
        "is_chain_valid": is_valid,
        "validation_status": validation_report["status"],
        "total_events": len(events),
        "events": events_dicts,
        "errors": validation_report.get("errors", [])
    }


@router.get("/all-events")
def get_all_custody_events(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(require_roles(["ADMIN", "AUDITOR", "INVESTIGATOR"]))
):
    events = db.query(CustodyEvent).order_by(CustodyEvent.created_at.desc()).offset(skip).limit(limit).all()
    return events
