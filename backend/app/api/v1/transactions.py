"""
Transaction Triage, SHAP Explanations, and Temporal Feature Inspection Endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import numpy as np

from backend.app.core.database import get_db
from backend.app.core.security import get_current_user, require_roles
from backend.app.schemas.case import TransactionAnalysisRequest, BatchAnalysisRequest
from backend.app.services.evidence_service import EvidenceService, ForensicPipelineRuntime
from backend.app.models.case import Evidence, Case
from forensic_engine.ml.pipeline import FEATURE_COLUMNS
from forensic_engine.risk_engine import compute_forensic_risk

router = APIRouter(prefix="/transactions", tags=["Transactions & AI Analysis"])


@router.post("/analyze")
def analyze_transaction(
    req: TransactionAnalysisRequest,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Real-time transaction risk scoring, anomaly detection, and SHAP explainability."""
    runtime = ForensicPipelineRuntime.get_instance()
    
    # Extract features using historical graph G(t-)
    features = runtime.graph_engine.extract_features_before_update(
        tx_id=req.transaction_id,
        src_wallet=req.source_wallet,
        dst_wallet=req.destination_wallet,
        amount=req.amount,
        timestamp=req.timestamp,
        assert_chronological=False
    )
    
    X_row = np.array([[features.get(c, 0.0) for c in FEATURE_COLUMNS]], dtype=np.float32)
    rf_risk = float(runtime.rf_model.predict_risk(X_row)[0])
    tree_preds = runtime.rf_model.get_individual_tree_predictions(X_row[0])
    anom_res = runtime.iforest_model.analyze_anomaly(X_row[0])
    
    risk_profile = compute_forensic_risk(
        rf_risk=rf_risk,
        anomaly_score=anom_res["anomaly_score"],
        features=features,
        tree_predictions=tree_preds
    )
    
    explanation = runtime.shap_explainer.explain_instance(
        X_sample=X_row[0],
        transaction_id=req.transaction_id,
        model_version=runtime.rf_model.version,
        risk_score=risk_profile["overall_risk"]
    )
    
    return {
        "transaction_id": req.transaction_id,
        "source_wallet": req.source_wallet,
        "destination_wallet": req.destination_wallet,
        "amount": req.amount,
        "timestamp": req.timestamp,
        "risk_profile": risk_profile,
        "explanation": explanation,
        "features": features
    }


@router.post("/batch-analyze")
def batch_analyze_transactions(
    req: BatchAnalysisRequest,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(require_roles(["ADMIN", "INVESTIGATOR"]))
):
    """Ingests and analyzes a batch of transactions chronologically."""
    results = []
    for tx in req.transactions:
        ev = EvidenceService.ingest_transaction_evidence(
            db=db,
            case_id=req.case_id,
            transaction_id=tx.transaction_id,
            source_wallet=tx.source_wallet,
            destination_wallet=tx.destination_wallet,
            amount=tx.amount,
            timestamp=tx.timestamp,
            source="BATCH_INGESTION",
            source_identifier=tx.source_identifier or "BATCH_01",
            actor=current_user["username"],
            role=current_user["role"]
        )
        results.append({
            "evidence_id": ev.evidence_id,
            "transaction_id": ev.transaction_id,
            "amount": ev.amount,
            "risk_score": ev.risk_score,
            "confidence": ev.confidence,
            "uncertainty_delta": ev.uncertainty_delta,
            "integrity_digest": ev.integrity_digest,
            "analyst_status": ev.analyst_status,
        })
    return {"status": "SUCCESS", "processed_count": len(results), "evidence_records": results}


@router.get("/{transaction_id}")
def get_transaction_detail(
    transaction_id: str,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    ev = db.query(Evidence).filter(Evidence.transaction_id == transaction_id).first()
    if not ev:
        raise HTTPException(status_code=404, detail="Transaction not found in forensic evidence records")
    return ev


@router.get("/{transaction_id}/explanation")
def get_transaction_explanation(
    transaction_id: str,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    ev = db.query(Evidence).filter(Evidence.transaction_id == transaction_id).first()
    if not ev:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return {
        "transaction_id": transaction_id,
        "evidence_id": ev.evidence_id,
        "risk_score": ev.risk_score,
        "explanation": ev.explanation_json,
        "corroboration": ev.corroboration_json,
        "features": ev.features_json
    }
