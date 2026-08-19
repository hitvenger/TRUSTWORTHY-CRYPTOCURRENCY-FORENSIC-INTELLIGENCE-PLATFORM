"""
Forensic Case Management Service for TCF-FX.
"""

import uuid
import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from backend.app.models.case import Case, Evidence
from backend.app.models.custody import CustodyEvent
from backend.app.schemas.case import CaseCreate
from forensic_engine.custody import create_custody_event, CustodyAction


class CaseService:
    @staticmethod
    def create_case(db: Session, case_in: CaseCreate, actor: str = "Lead Investigator", role: str = "INVESTIGATOR") -> Case:
        case_id = f"case_{uuid.uuid4().hex[:10]}"
        db_case = Case(
            case_id=case_id,
            title=case_in.title,
            description=case_in.description,
            investigator=case_in.investigator or actor,
            priority=case_in.priority or "HIGH",
            tags=case_in.tags or [],
            status="ACTIVE"
        )
        db.add(db_case)
        db.commit()
        db.refresh(db_case)

        # Log genesis custody event for case
        genesis_evt = create_custody_event(
            case_id=case_id,
            actor=actor,
            role=role,
            action=CustodyAction.CASE_CREATED,
            metadata={"title": db_case.title, "priority": db_case.priority}
        )
        db_custody = CustodyEvent(
            event_id=genesis_evt["event_id"],
            case_id=genesis_evt["case_id"],
            evidence_id=None,
            actor=genesis_evt["actor"],
            role=genesis_evt["role"],
            action=genesis_evt["action"],
            timestamp=genesis_evt["timestamp"],
            metadata_json=genesis_evt["metadata"],
            previous_hash=genesis_evt["previous_hash"],
            event_hash=genesis_evt["event_hash"]
        )
        db.add(db_custody)
        db.commit()

        return db_case

    @staticmethod
    def get_case(db: Session, case_id: str) -> Optional[Case]:
        return db.query(Case).filter(Case.case_id == case_id).first()

    @staticmethod
    def list_cases(db: Session, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        cases = db.query(Case).offset(skip).limit(limit).all()
        results = []
        for c in cases:
            ev_count = db.query(Evidence).filter(Evidence.case_id == c.case_id).count()
            high_risk_count = db.query(Evidence).filter(
                Evidence.case_id == c.case_id,
                Evidence.risk_score >= 0.70
            ).count()
            results.append({
                "case_id": c.case_id,
                "title": c.title,
                "description": c.description,
                "investigator": c.investigator,
                "status": c.status,
                "priority": c.priority,
                "tags": c.tags or [],
                "evidence_count": ev_count,
                "high_risk_lead_count": high_risk_count,
                "created_at": c.created_at,
                "updated_at": c.updated_at
            })
        return results

    @staticmethod
    def update_case_status(db: Session, case_id: str, new_status: str, actor: str = "Lead Investigator", role: str = "INVESTIGATOR") -> Optional[Case]:
        c = db.query(Case).filter(Case.case_id == case_id).first()
        if not c:
            return None
        old_status = c.status
        c.status = new_status
        db.commit()
        db.refresh(c)

        # Log custody event
        last_evt = db.query(CustodyEvent).filter(CustodyEvent.case_id == case_id).order_by(CustodyEvent.created_at.desc()).first()
        prev_hash = last_evt.event_hash if last_evt else None

        evt = create_custody_event(
            case_id=case_id,
            actor=actor,
            role=role,
            action=CustodyAction.CASE_STATUS_CHANGED,
            previous_hash=prev_hash,
            metadata={"prior_status": old_status, "new_status": new_status}
        )
        db_custody = CustodyEvent(
            event_id=evt["event_id"],
            case_id=evt["case_id"],
            evidence_id=None,
            actor=evt["actor"],
            role=evt["role"],
            action=evt["action"],
            timestamp=evt["timestamp"],
            metadata_json=evt["metadata"],
            previous_hash=evt["previous_hash"],
            event_hash=evt["event_hash"]
        )
        db.add(db_custody)
        db.commit()

        return c
