"""
Dashboard Aggregated Metrics API Endpoints.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any, List

from backend.app.core.database import get_db
from backend.app.core.security import get_current_user
from backend.app.models.case import Case, Evidence
from backend.app.models.custody import CustodyEvent, AnalystReview
from backend.app.services.evidence_service import ForensicPipelineRuntime

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary")
def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    open_cases = db.query(Case).filter(Case.status == "ACTIVE").count()
    total_evidence = db.query(Evidence).count()
    high_risk_leads = db.query(Evidence).filter(Evidence.risk_score >= 0.65).count()
    critical_leads = db.query(Evidence).filter(Evidence.risk_score >= 0.80).count()
    tamper_alerts = db.query(Evidence).filter(Evidence.is_tampered == True).count()
    review_queue_count = db.query(Evidence).filter(Evidence.analyst_status == "MODEL_LEAD", Evidence.risk_score >= 0.60).count()
    total_custody_events = db.query(CustodyEvent).count()
    confirmed_findings = db.query(AnalystReview).filter(AnalystReview.new_state == "FORENSIC_FINDING").count()
    anchored_evidence_count = db.query(Evidence).filter(Evidence.is_anchored == True).count()

    # Risk Distribution Breakdown
    risk_low = db.query(Evidence).filter(Evidence.risk_score < 0.35).count()
    risk_med = db.query(Evidence).filter(Evidence.risk_score >= 0.35, Evidence.risk_score < 0.60).count()
    risk_high = db.query(Evidence).filter(Evidence.risk_score >= 0.60, Evidence.risk_score < 0.80).count()
    risk_crit = db.query(Evidence).filter(Evidence.risk_score >= 0.80).count()

    # Recent High-Priority Leads
    recent_leads = db.query(Evidence).order_by(Evidence.created_at.desc()).limit(8).all()

    return {
        "metrics": {
            "open_cases": open_cases,
            "total_evidence": total_evidence,
            "high_risk_leads": high_risk_leads,
            "critical_leads": critical_leads,
            "integrity_tamper_alerts": tamper_alerts,
            "analyst_review_queue": review_queue_count,
            "total_custody_events": total_custody_events,
            "confirmed_findings": confirmed_findings,
            "anchored_on_chain": anchored_evidence_count,
        },
        "risk_distribution": {
            "low": risk_low,
            "medium": risk_med,
            "high": risk_high,
            "critical": risk_crit
        },
        "recent_leads": [
            {
                "evidence_id": e.evidence_id,
                "case_id": e.case_id,
                "transaction_id": e.transaction_id,
                "amount": e.amount,
                "risk_score": e.risk_score,
                "confidence": e.confidence,
                "uncertainty_delta": e.uncertainty_delta,
                "analyst_status": e.analyst_status,
                "is_tampered": e.is_tampered,
                "is_anchored": e.is_anchored,
                "timestamp": e.event_timestamp or e.acquisition_timestamp
            }
            for e in recent_leads
        ]
    }
