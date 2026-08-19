"""
Forensic Report Export Endpoints (PDF, JSON Manifest, CSV).
"""

from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import JSONResponse, PlainTextResponse
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional

from backend.app.core.database import get_db
from backend.app.core.security import get_current_user, require_roles
from backend.app.schemas.custody import ReportGenerateRequest
from backend.app.services.report_service import ReportService
from backend.app.models.case import Case, Evidence
from backend.app.models.custody import CustodyEvent
from forensic_engine.custody import create_custody_event, CustodyAction

router = APIRouter(prefix="/reports", tags=["Forensic Reports"])


@router.post("/generate")
def generate_report(
    req: ReportGenerateRequest,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(require_roles(["ADMIN", "INVESTIGATOR", "ANALYST"]))
):
    case = db.query(Case).filter(Case.case_id == req.case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    manifest = ReportService.generate_json_manifest(db, req.case_id)
    
    # Record custody event for report generation
    last_evt = db.query(CustodyEvent).filter(CustodyEvent.case_id == req.case_id).order_by(CustodyEvent.created_at.desc()).first()
    prev_h = last_evt.event_hash if last_evt else None
    evt = create_custody_event(
        case_id=req.case_id,
        actor=current_user["username"],
        role=current_user["role"],
        action=CustodyAction.REPORT_GENERATED,
        previous_hash=prev_h,
        metadata={"title": req.report_title}
    )
    db_evt = CustodyEvent(
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
    db.add(db_evt)
    db.commit()

    return {
        "status": "SUCCESS",
        "case_id": req.case_id,
        "report_title": req.report_title,
        "available_formats": ["PDF", "JSON_MANIFEST", "CSV"],
        "manifest_summary": {
            "evidence_count": len(manifest["evidence_inventory"]),
            "custody_event_count": len(manifest["chain_of_custody_events"]),
            "analyst_review_count": len(manifest["analyst_reviews"])
        }
    }


@router.get("/{case_id}/manifest")
def download_manifest(
    case_id: str,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    try:
        manifest = ReportService.generate_json_manifest(db, case_id)
        return JSONResponse(content=manifest)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{case_id}/csv")
def download_csv(
    case_id: str,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    try:
        csv_data = ReportService.generate_csv_export(db, case_id)
        return Response(
            content=csv_data,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=case_{case_id}_evidence.csv"}
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{case_id}/pdf")
def download_pdf(
    case_id: str,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    try:
        pdf_bytes = ReportService.generate_pdf_report(db, case_id)
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=case_{case_id}_forensic_report.pdf"}
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
