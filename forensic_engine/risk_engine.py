"""
Forensic Risk Fusion Engine for TCF-FX.

Integrates supervised classifier outputs, unsupervised anomaly scores, graph topology metrics,
temporal velocity patterns, and independent corroboration into a calibrated investigative risk assessment.

NOTE: Risk levels indicate INVESTIGATIVE PRIORITY, NOT LEGAL GUILT.
"""

from typing import Dict, Any, Optional
from forensic_engine.uncertainty import compute_uncertainty_metrics
from forensic_engine.corroboration import evaluate_corroboration


def compute_forensic_risk(
    rf_risk: float,
    anomaly_score: float = 0.0,
    xgb_risk: Optional[float] = None,
    gnn_risk: Optional[float] = None,
    features: Optional[Dict[str, float]] = None,
    evidence_verified: bool = True,
    has_provenance: bool = True,
    tree_predictions: Optional[list] = None,
) -> Dict[str, Any]:
    """
    Synthesizes multiple orthogonal analytical signals into a unified forensic risk profile.
    """
    features = features or {}
    
    # 1. Temporal Risk Component
    velocity = features.get("src_tx_velocity_hourly", 0.0)
    rapid_drain = features.get("rapid_drain_indicator", 0.0)
    temporal_risk = min(1.0, (velocity / 20.0) * 0.5 + rapid_drain * 0.5)
    
    # 2. Graph Risk Component
    k_hop_exp = features.get("k_hop_suspicious_exposure", 0.0)
    clustering = features.get("src_clustering_coefficient", 0.0)
    graph_risk = min(1.0, k_hop_exp * 0.7 + clustering * 0.3)
    if gnn_risk is not None:
        graph_risk = (graph_risk * 0.4) + (gnn_risk * 0.6)

    # 3. Supervised Model Risk (RF weighted with XGB if available)
    if xgb_risk is not None:
        supervised_risk = (rf_risk * 0.6) + (xgb_risk * 0.4)
    else:
        supervised_risk = rf_risk

    # 4. Evaluate Corroboration independently
    corroboration = evaluate_corroboration(
        features=features,
        model_risk=supervised_risk,
        anomaly_score=anomaly_score,
        graph_risk=graph_risk
    )
    corroboration_score = corroboration["score"]

    # 5. Risk Fusion Formula
    # Weights: Supervised (0.45), Anomaly (0.20), Graph (0.15), Temporal (0.10), Corroboration (0.10)
    fused_risk = (
        (supervised_risk * 0.45) +
        (anomaly_score * 0.20) +
        (graph_risk * 0.15) +
        (temporal_risk * 0.10) +
        (corroboration_score * 0.10)
    )
    
    # If evidence is tampered, flag immediately
    if not evidence_verified:
        fused_risk = max(fused_risk, 0.85)

    fused_risk = round(float(min(1.0, max(0.0, fused_risk))), 4)

    # 6. Map to Forensic Investigative Priority (Risk Level)
    if fused_risk >= 0.80 or (fused_risk >= 0.70 and corroboration["status"] == "STRONG"):
        risk_level = "CRITICAL"
        priority_rank = 1
        priority_description = "Immediate investigative triage required. Multiple corroborating indicators present."
    elif fused_risk >= 0.60:
        risk_level = "HIGH"
        priority_rank = 2
        priority_description = "High investigative priority. Elevated analytical risk and anomaly alignment."
    elif fused_risk >= 0.35:
        risk_level = "MEDIUM"
        priority_rank = 3
        priority_description = "Moderate investigative priority. Review when primary leads are resolved."
    else:
        risk_level = "LOW"
        priority_rank = 4
        priority_description = "Routine baseline activity. Low investigative priority."

    # 7. Compute Uncertainty Breakdown
    uncertainty_info = compute_uncertainty_metrics(
        model_prob=fused_risk,
        tree_predictions=tree_predictions,
        anomaly_score=anomaly_score,
        evidence_verified=evidence_verified,
        has_provenance=has_provenance,
        corroboration_score=corroboration_score
    )

    return {
        "overall_risk": fused_risk,
        "risk_level": risk_level,
        "investigative_priority": priority_rank,
        "priority_description": priority_description,
        "subscores": {
            "rf_risk": round(rf_risk, 4),
            "anomaly_score": round(anomaly_score, 4),
            "xgb_risk": round(xgb_risk, 4) if xgb_risk is not None else None,
            "gnn_risk": round(gnn_risk, 4) if gnn_risk is not None else None,
            "graph_risk": round(graph_risk, 4),
            "temporal_risk": round(temporal_risk, 4),
            "corroboration_score": round(corroboration_score, 4),
        },
        "uncertainty": uncertainty_info,
        "corroboration": corroboration,
        "forensic_disclaimer": "AI risk score indicates investigative triage priority and does NOT constitute a proven legal finding."
    }
