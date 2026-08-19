"""
Forensic Evidence Management & Analytical Pipeline Service for TCF-FX.
"""

import uuid
import datetime
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session

from backend.app.models.case import Case, Evidence
from backend.app.models.custody import CustodyEvent
from forensic_engine.canonical import canonical_json_dumps, canonical_json_bytes
from forensic_engine.hashing import create_digest, verify_digest, detect_tampering
from forensic_engine.custody import create_custody_event, CustodyAction
from forensic_engine.temporal_graph import IncrementalTemporalGraph
from forensic_engine.ml.random_forest import ForensicRandomForest
from forensic_engine.ml.isolation_forest import ForensicIsolationForest
from forensic_engine.ml.pipeline import FEATURE_COLUMNS
from forensic_engine.explainability.shap_engine import ForensicShapExplainer
from forensic_engine.risk_engine import compute_forensic_risk
from datasets.synthetic import generate_synthetic_dataset


class ForensicPipelineRuntime:
    """Singleton runtime maintaining active temporal graph and trained models."""
    _instance = None

    def __init__(self):
        self.graph_engine = IncrementalTemporalGraph()
        self.rf_model = ForensicRandomForest(random_state=42)
        self.iforest_model = ForensicIsolationForest(random_state=42)
        self.shap_explainer = None
        self.is_initialized = False
        self._bootstrap_models()

    def _bootstrap_models(self):
        """Initializes and pre-trains models on baseline calibration data."""
        # Generate 1500 calibration samples
        calib_txs = generate_synthetic_dataset(num_transactions=1500, seed=42)
        enriched = self.graph_engine.process_transaction_stream(calib_txs)
        
        X_list = []
        y_list = []
        for tx in enriched:
            feats = tx["features"]
            X_list.append([feats.get(c, 0.0) for c in FEATURE_COLUMNS])
            y_list.append(int(tx.get("label", 0)))
            
        X = np.array(X_list, dtype=np.float32)
        y = np.array(y_list, dtype=np.int32)
        
        self.rf_model.fit(X, y, feature_names=FEATURE_COLUMNS)
        self.iforest_model.fit(X, feature_names=FEATURE_COLUMNS)
        self.shap_explainer = ForensicShapExplainer(
            model=self.rf_model,
            feature_names=FEATURE_COLUMNS,
            background_data=X[:100]
        )
        self.is_initialized = True

    @classmethod
    def get_instance(cls) -> "ForensicPipelineRuntime":
        if cls._instance is None:
            cls._instance = ForensicPipelineRuntime()
        return cls._instance


class EvidenceService:
    @staticmethod
    def ingest_transaction_evidence(
        db: Session,
        case_id: str,
        transaction_id: str,
        source_wallet: str,
        destination_wallet: str,
        amount: float,
        timestamp: float,
        source: str = "BLOCKCHAIN_INGESTION",
        source_identifier: str = "MAINNET_NODE_01",
        actor: str = "Lead Investigator",
        role: str = "INVESTIGATOR"
    ) -> Evidence:
        runtime = ForensicPipelineRuntime.get_instance()
        
        # 1. Anti-Leakage Feature Extraction G(t-)
        features = runtime.graph_engine.extract_features_before_update(
            tx_id=transaction_id,
            src_wallet=source_wallet,
            dst_wallet=destination_wallet,
            amount=amount,
            timestamp=timestamp,
            assert_chronological=False
        )

        X_row = np.array([[features.get(c, 0.0) for c in FEATURE_COLUMNS]], dtype=np.float32)

        # 2. AI Analytical Scoring
        rf_risk = float(runtime.rf_model.predict_risk(X_row)[0])
        tree_preds = runtime.rf_model.get_individual_tree_predictions(X_row[0])
        anom_res = runtime.iforest_model.analyze_anomaly(X_row[0])
        anomaly_score = anom_res["anomaly_score"]

        # 3. Risk Engine Multi-Signal Fusion
        risk_profile = compute_forensic_risk(
            rf_risk=rf_risk,
            anomaly_score=anomaly_score,
            features=features,
            evidence_verified=True,
            has_provenance=True,
            tree_predictions=tree_preds
        )

        # 4. Generate SHAP Explanation
        evidence_id = f"ev_{uuid.uuid4().hex[:12]}"
        explanation = runtime.shap_explainer.explain_instance(
            X_sample=X_row[0],
            transaction_id=transaction_id,
            evidence_id=evidence_id,
            model_version=runtime.rf_model.version,
            risk_score=risk_profile["overall_risk"]
        )

        # 5. Update Temporal Graph G(t)
        is_suspicious = bool(risk_profile["overall_risk"] >= 0.65)
        runtime.graph_engine.update_graph(
            tx_id=transaction_id,
            src_wallet=source_wallet,
            dst_wallet=destination_wallet,
            amount=amount,
            timestamp=timestamp,
            is_suspicious_lead=is_suspicious
        )

        # 6. Build Canonical Evidence Record and Compute SHA-256 Digest
        acq_ts = datetime.datetime.now(datetime.timezone.utc).isoformat()
        canonical_payload = {
            "evidence_id": evidence_id,
            "case_id": case_id,
            "evidence_type": "CRYPTOCURRENCY_TRANSACTION",
            "source": source,
            "source_identifier": source_identifier,
            "acquisition_timestamp": acq_ts,
            "event_timestamp": str(timestamp),
            "transaction_id": transaction_id,
            "source_wallet": source_wallet,
            "destination_wallet": destination_wallet,
            "amount": amount,
            "feature_schema_version": "1.0.0",
            "model_id": runtime.rf_model.model_id,
            "model_version": runtime.rf_model.version,
            "risk_score": risk_profile["overall_risk"],
            "anomaly_score": anomaly_score,
            "confidence": risk_profile["uncertainty"]["model_confidence_level"],
            "uncertainty_delta": risk_profile["uncertainty"]["uncertainty_delta"],
        }
        digest = create_digest(canonical_payload)

        # 7. Persist Evidence DB entity
        db_ev = Evidence(
            evidence_id=evidence_id,
            case_id=case_id,
            evidence_type="CRYPTOCURRENCY_TRANSACTION",
            source=source,
            source_identifier=source_identifier,
            acquisition_timestamp=acq_ts,
            event_timestamp=str(timestamp),
            transaction_id=transaction_id,
            source_wallet=source_wallet,
            destination_wallet=destination_wallet,
            amount=amount,
            feature_schema_version="1.0.0",
            model_id=runtime.rf_model.model_id,
            model_version=runtime.rf_model.version,
            risk_score=risk_profile["overall_risk"],
            anomaly_score=anomaly_score,
            graph_score=risk_profile["subscores"]["graph_risk"],
            temporal_score=risk_profile["subscores"]["temporal_risk"],
            confidence=risk_profile["uncertainty"]["model_confidence_level"],
            uncertainty_delta=risk_profile["uncertainty"]["uncertainty_delta"],
            explanation_json=explanation,
            corroboration_json=risk_profile["corroboration"],
            features_json=features,
            analyst_status="MODEL_LEAD",
            integrity_digest=digest,
            is_tampered=False
        )
        db.add(db_ev)
        db.commit()
        db.refresh(db_ev)

        # 8. Record Chained Custody Events
        last_evt = db.query(CustodyEvent).filter(CustodyEvent.case_id == case_id).order_by(CustodyEvent.created_at.desc()).first()
        prev_h = last_evt.event_hash if last_evt else None

        # Acquisition Event
        evt_acq = create_custody_event(
            case_id=case_id,
            evidence_id=evidence_id,
            actor=actor,
            role=role,
            action=CustodyAction.EVIDENCE_ACQUIRED,
            previous_hash=prev_h,
            metadata={"transaction_id": transaction_id, "amount": amount, "digest": digest}
        )
        db_acq = CustodyEvent(
            event_id=evt_acq["event_id"],
            case_id=evt_acq["case_id"],
            evidence_id=evt_acq["evidence_id"],
            actor=evt_acq["actor"],
            role=evt_acq["role"],
            action=evt_acq["action"],
            timestamp=evt_acq["timestamp"],
            metadata_json=evt_acq["metadata"],
            previous_hash=evt_acq["previous_hash"],
            event_hash=evt_acq["event_hash"]
        )
        db.add(db_acq)
        db.commit()

        return db_ev

    @staticmethod
    def verify_evidence(db: Session, evidence_id: str) -> Dict[str, Any]:
        ev = db.query(Evidence).filter(Evidence.evidence_id == evidence_id).first()
        if not ev:
            return {"status": "NOT_FOUND", "is_valid": False}

        canonical_payload = {
            "evidence_id": ev.evidence_id,
            "case_id": ev.case_id,
            "evidence_type": ev.evidence_type,
            "source": ev.source,
            "source_identifier": ev.source_identifier,
            "acquisition_timestamp": ev.acquisition_timestamp,
            "event_timestamp": ev.event_timestamp,
            "transaction_id": ev.transaction_id,
            "source_wallet": ev.source_wallet,
            "destination_wallet": ev.destination_wallet,
            "amount": ev.amount,
            "feature_schema_version": ev.feature_schema_version,
            "model_id": ev.model_id,
            "model_version": ev.model_version,
            "risk_score": ev.risk_score,
            "anomaly_score": ev.anomaly_score,
            "confidence": ev.confidence,
            "uncertainty_delta": ev.uncertainty_delta,
        }
        is_valid, computed, meta = verify_digest(canonical_payload, expected_digest=ev.integrity_digest)
        return {
            "evidence_id": evidence_id,
            "is_valid": is_valid,
            "status": "INTEGRITY_VERIFIED" if is_valid else "TAMPER_DETECTED",
            "expected_digest": ev.integrity_digest,
            "computed_digest": computed,
            "is_flagged_tampered_in_db": ev.is_tampered
        }

    @staticmethod
    def simulate_tampering(db: Session, evidence_id: str, field_name: str, new_value: Any) -> Dict[str, Any]:
        """Deliberately mutates a field in an evidence record to test cryptographic tamper detection."""
        ev = db.query(Evidence).filter(Evidence.evidence_id == evidence_id).first()
        if not ev:
            return {"error": "Evidence not found"}

        old_val = getattr(ev, field_name, None)
        setattr(ev, field_name, new_value)
        ev.is_tampered = True
        db.commit()
        db.refresh(ev)

        # Verify to demonstrate failure
        verification = EvidenceService.verify_evidence(db, evidence_id)
        return {
            "status": "TAMPER_SIMULATED",
            "evidence_id": evidence_id,
            "tampered_field": field_name,
            "original_value": old_val,
            "injected_value": new_value,
            "verification_result": verification
        }

    @staticmethod
    def restore_evidence(db: Session, evidence_id: str, field_name: str, original_value: Any) -> Dict[str, Any]:
        """Restores original value and verifies recovery."""
        ev = db.query(Evidence).filter(Evidence.evidence_id == evidence_id).first()
        if not ev:
            return {"error": "Evidence not found"}

        setattr(ev, field_name, original_value)
        ev.is_tampered = False
        db.commit()
        db.refresh(ev)

        verification = EvidenceService.verify_evidence(db, evidence_id)
        return {
            "status": "EVIDENCE_RESTORED",
            "evidence_id": evidence_id,
            "restored_field": field_name,
            "restored_value": original_value,
            "verification_result": verification
        }
