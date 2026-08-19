"""
Analyst Review & Forensic Findings Promotion Endpoints for TCF-FX.

Enforces:
AI OUTPUT != FORENSIC FINDING != LEGAL CONCLUSION
Promotes AI leads to confirmed forensic findings only after qualified human review.
"""

import uuid
import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional

from backend.app.core.database import get_db
from backend.app.core.security import get_current_user, require_roles
from backend.app.schemas.custody import AnalystReviewCreate, AnalystReviewResponse
from backend.app.models.case import Evidence, Case
from backend.app.models.custody import AnalystReview, CustodyEvent
from forensic_engine.custody import create_custody_event, CustodyAction

router = APIRouter(prefix="/analyst-review", tags=["Analyst Review & Findings"])


@router.post("", response_model=Dict[str, Any])
def submit_analyst_review(
    req: AnalystReviewCreate,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(require_roles(["ADMIN", "INVESTIGATOR", "ANALYST"]))
):
    ev = db.query(Evidence).filter(Evidence.evidence_id == req.evidence_id).first()
    if not ev:
        raise HTTPException(status_code=404, detail="Evidence item not found")

    prior_state = ev.analyst_status
    new_state = req.new_state.upper()

    # Update evidence record
    ev.analyst_status = new_state
    ev.analyst_comment = req.finding_summary
    ev.analyst_name = current_user["username"]
    db.commit()

    # Create Analyst Review DB record
    review_id = f"rev_{uuid.uuid4().hex[:10]}"
    review = AnalystReview(
        review_id=review_id,
        case_id=req.case_id,
        evidence_id=req.evidence_id,
        transaction_id=ev.transaction_id,
        analyst_name=current_user["username"],
        role=current_user["role"],
        prior_state=prior_state,
        new_state=new_state,
        finding_summary=req.finding_summary,
        rationale=req.rationale,
        corroborating_notes=req.corroborating_notes
    )
    db.add(review)
    db.commit()

    # Record chained custody event
    last_evt = db.query(CustodyEvent).filter(CustodyEvent.case_id == req.case_id).order_by(CustodyEvent.created_at.desc()).first()
    prev_h = last_evt.event_hash if last_evt else None
    evt = create_custody_event(
        case_id=req.case_id,
        evidence_id=req.evidence_id,
        actor=current_user["username"],
        role=current_user["role"],
        action=CustodyAction.ANALYST_DECISION,
        previous_hash=prev_h,
        metadata={
            "prior_state": prior_state,
            "new_state": new_state,
            "finding": req.finding_summary,
            "review_id": review_id
        }
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
        "status": "SUCCESS",
        "message": f"Review recorded: Evidence promoted to {new_state}",
        "review_id": review_id,
        "evidence_id": req.evidence_id,
        "prior_state": prior_state,
        "new_state": new_state,
        "event_hash": evt["event_hash"]
    }


@router.get("/case/{case_id}")
def get_case_reviews(
    case_id: str,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    reviews = db.query(AnalystReview).filter(AnalystReview.case_id == case_id).order_by(AnalystReview.created_at.desc()).all()
    return reviews
