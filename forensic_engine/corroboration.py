"""
Forensic Corroboration Engine for TCF-FX.

Evaluates independent orthogonal investigative signals to corroborate or challenge
AI model classifications, preventing single-model bias from dictating findings.
"""

from typing import Dict, Any, List, Tuple


def evaluate_corroboration(
    features: Dict[str, float],
    model_risk: float,
    anomaly_score: float,
    graph_risk: float = 0.0,
    has_prior_flagged_counterparty: bool = False,
) -> Dict[str, Any]:
    """
    Evaluates rule-aware multi-signal corroboration for a given transaction.
    """
    indicators = []
    contra_indicators = []
    
    # Signal 1: Transaction Velocity Burst
    velocity = features.get("src_tx_velocity_hourly", 0.0)
    past_1h_txs = features.get("src_past_1h_txs", 0.0)
    if velocity > 15.0 or past_1h_txs > 10:
        indicators.append({
            "code": "IND_VELOCITY_BURST",
            "title": "High Transaction Velocity Burst",
            "description": f"Source wallet exhibited abnormal velocity ({int(past_1h_txs)} txs in past hour).",
            "weight": 0.25
        })
        
    # Signal 2: Rapid Transfer / Peeling / Drain Sequence
    rapid_drain = features.get("rapid_drain_indicator", 0.0)
    time_since_last = features.get("src_time_since_last_tx", 9999.0)
    if rapid_drain > 0.5 or (0 < time_since_last < 180):
        indicators.append({
            "code": "IND_RAPID_DRAIN",
            "title": "Rapid Downstream Transfer Sequence",
            "description": "Immediate outgoing transaction observed following recent incoming fund movement.",
            "weight": 0.25
        })

    # Signal 3: Counterparty Concentration / Flagged Exposure
    suspicious_exposure = features.get("k_hop_suspicious_exposure", 0.0)
    if suspicious_exposure > 0.3 or has_prior_flagged_counterparty:
        indicators.append({
            "code": "IND_FLAGGED_EXPOSURE",
            "title": "Topological Exposure to Flagged Clusters",
            "description": f"Wallet has direct topological proximity ({round(suspicious_exposure*100, 1)}%) to known suspicious nodes.",
            "weight": 0.30
        })

    # Signal 4: Unsupervised Anomaly Alignment
    if anomaly_score >= 0.65:
        indicators.append({
            "code": "IND_UNSUPERVISED_ANOMALY",
            "title": "Independent Anomaly Signal Alignment",
            "description": f"Isolation Forest independently detected high multi-dimensional anomaly (Score: {round(anomaly_score, 2)}).",
            "weight": 0.20
        })

    # Signal 5: Dormant Reactivation
    is_dormant = features.get("src_is_dormant_reactivation", 0.0)
    if is_dormant > 0.5:
        indicators.append({
            "code": "IND_DORMANT_REACTIVATION",
            "title": "Dormant Wallet Reactivation",
            "description": "Wallet was inactive for >7 days before executing sudden substantial transfer.",
            "weight": 0.15
        })
        
    # Signal 6: Topological Out-Degree Asymmetry (Fan-out mixing)
    out_degree = features.get("src_out_degree", 0.0)
    in_degree = features.get("src_in_degree", 0.0)
    if out_degree > 12 and (out_degree / max(1.0, in_degree)) > 4.0:
        indicators.append({
            "code": "IND_FAN_OUT_DISPERSAL",
            "title": "High-Degree Fan-Out Dispersal",
            "description": "High asymmetric out-degree indicates automated fund dispersal/mixing pattern.",
            "weight": 0.20
        })

    # Contra-indicators (Signals suggesting benign / routine behavior)
    counterparty_diversity = features.get("src_counterparty_diversity", 0.0)
    wallet_age_days = features.get("src_wallet_age_seconds", 0.0) / 86400.0
    if wallet_age_days > 180 and counterparty_diversity > 0.7 and anomaly_score < 0.2:
        contra_indicators.append({
            "code": "CONTRA_ESTABLISHED_BENIGN",
            "title": "Established Organic History",
            "description": f"Matured wallet ({int(wallet_age_days)} days) with diverse organic counterparties.",
            "weight": 0.30
        })

    # Compute aggregate corroboration weight
    total_support_weight = sum(ind["weight"] for ind in indicators)
    total_contra_weight = sum(cind["weight"] for cind in contra_indicators)
    
    corroboration_score = max(0.0, min(1.0, total_support_weight - (0.5 * total_contra_weight)))
    
    count = len(indicators)
    if count >= 3 or corroboration_score >= 0.65:
        status = "STRONG"
    elif count == 2 or corroboration_score >= 0.40:
        status = "MODERATE"
    elif count == 1 or corroboration_score >= 0.15:
        status = "WEAK"
    else:
        status = "NONE"

    return {
        "status": status,
        "score": round(corroboration_score, 4),
        "supporting_indicator_count": len(indicators),
        "supporting_indicators": indicators,
        "contra_indicators": contra_indicators,
        "explanation": f"{status} corroboration with {len(indicators)} supporting indicators."
    }
