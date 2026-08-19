"""
Case Management Endpoints for TCF-FX API.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional

from backend.app.core.database import get_db
from backend.app.core.security import get_current_user, require_roles
from backend.app.schemas.case import CaseCreate, CaseResponse
from backend.app.services.case_service import CaseService
from backend.app.models.case import Evidence

router = APIRouter(prefix="/cases", tags=["Cases"])


@router.post("", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
def create_case(
    case_in: CaseCreate,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(require_roles(["ADMIN", "INVESTIGATOR"]))
):
    case = CaseService.create_case(
        db=db,
        case_in=case_in,
        actor=current_user["username"],
        role=current_user["role"]
    )
    return {
        "status": "SUCCESS",
        "message": f"Forensic Case {case.case_id} initialized",
        "case": {
            "case_id": case.case_id,
            "title": case.title,
            "description": case.description,
            "investigator": case.investigator,
            "status": case.status,
            "priority": case.priority,
            "tags": case.tags,
            "created_at": case.created_at
        }
    }


@router.get("", response_model=List[Dict[str, Any]])
def list_cases(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    return CaseService.list_cases(db=db, skip=skip, limit=limit)


@router.get("/{case_id}")
def get_case(
    case_id: str,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    case = CaseService.get_case(db=db, case_id=case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    evidence_count = db.query(Evidence).filter(Evidence.case_id == case_id).count()
    return {
        "case_id": case.case_id,
        "title": case.title,
        "description": case.description,
        "investigator": case.investigator,
        "status": case.status,
        "priority": case.priority,
        "tags": case.tags,
        "evidence_count": evidence_count,
        "created_at": case.created_at,
        "updated_at": case.updated_at
    }


@router.patch("/{case_id}/status")
def update_case_status(
    case_id: str,
    status_payload: Dict[str, str],
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(require_roles(["ADMIN", "INVESTIGATOR", "ANALYST"]))
):
    new_status = status_payload.get("status")
    if not new_status:
        raise HTTPException(status_code=400, detail="Missing new status in payload")
    
    updated = CaseService.update_case_status(
        db=db,
        case_id=case_id,
        new_status=new_status,
        actor=current_user["username"],
        role=current_user["role"]
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Case not found")
    return {"status": "SUCCESS", "case_id": case_id, "new_status": updated.status}
