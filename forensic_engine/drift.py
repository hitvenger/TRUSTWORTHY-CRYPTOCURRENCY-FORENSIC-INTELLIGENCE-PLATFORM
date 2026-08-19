"""
Forensic Model & Data Drift Monitor for TCF-FX.

Calculates Population Stability Index (PSI) and distribution shifts across
incoming forensic batches to ensure analytical model validity over time.
"""

import numpy as np
from typing import Dict, List, Any, Tuple


def calculate_psi(expected: np.ndarray, actual: np.ndarray, num_buckets: int = 10) -> float:
    """
    Computes Population Stability Index (PSI) between baseline and current distributions.
    PSI < 0.1: No significant change (NORMAL)
    0.1 <= PSI < 0.25: Moderate shift (WATCH)
    PSI >= 0.25: Significant distributional shift (DRIFT_DETECTED)
    """
    if len(expected) == 0 or len(actual) == 0:
        return 0.0
    
    # Generate quantile-based bucket breaks from baseline
    quantiles = np.linspace(0, 100, num_buckets + 1)
    percentiles = np.percentile(expected, quantiles)
    percentiles[0] = -np.inf
    percentiles[-1] = np.inf
    
    # Calculate counts per bucket
    expected_counts, _ = np.histogram(expected, bins=percentiles)
    actual_counts, _ = np.histogram(actual, bins=percentiles)
    
    # Avoid zero division with Laplace smoothing
    expected_pct = (expected_counts + 1e-4) / (len(expected) + 1e-4 * num_buckets)
    actual_pct = (actual_counts + 1e-4) / (len(actual) + 1e-4 * num_buckets)
    
    # PSI summation: sum((actual - expected) * ln(actual / expected))
    psi_value = np.sum((actual_pct - expected_pct) * np.log(actual_pct / expected_pct))
    return float(max(0.0, psi_value))


def analyze_drift(
    baseline_features: Dict[str, List[float]],
    current_features: Dict[str, List[float]],
    baseline_scores: List[float],
    current_scores: List[float]
) -> Dict[str, Any]:
    """
    Performs comprehensive drift analysis across features, risk scores, and graph dynamics.
    """
    feature_drift_results = {}
    total_psi = 0.0
    num_features = 0
    
    for feat_name, base_vals in baseline_features.items():
        curr_vals = current_features.get(feat_name, [])
        if len(base_vals) >= 20 and len(curr_vals) >= 20:
            psi = calculate_psi(np.array(base_vals), np.array(curr_vals))
            status = "NORMAL" if psi < 0.10 else ("WATCH" if psi < 0.25 else "DRIFT_DETECTED")
            feature_drift_results[feat_name] = {
                "psi": round(psi, 4),
                "status": status,
                "baseline_mean": round(float(np.mean(base_vals)), 4),
                "current_mean": round(float(np.mean(curr_vals)), 4),
            }
            total_psi += psi
            num_features += 1

    # Score drift
    score_psi = calculate_psi(np.array(baseline_scores), np.array(current_scores)) if (len(baseline_scores) >= 20 and len(current_scores) >= 20) else 0.0
    score_status = "NORMAL" if score_psi < 0.10 else ("WATCH" if score_psi < 0.25 else "DRIFT_DETECTED")
    
    avg_feat_psi = (total_psi / max(1, num_features)) if num_features > 0 else 0.0
    
    # Overall system status
    max_psi = max(score_psi, avg_feat_psi)
    if max_psi >= 0.25:
        overall_status = "DRIFT_DETECTED"
        recommendation = "Analytical drift detected. Administrative review required for model recalibration."
    elif max_psi >= 0.10:
        overall_status = "WATCH"
        recommendation = "Moderate distributional shift detected. Monitor incoming batches closely."
    else:
        overall_status = "NORMAL"
        recommendation = "Data and prediction distributions are aligned with baseline training regime."

    return {
        "status": overall_status,
        "score_drift": {
            "psi": round(score_psi, 4),
            "status": score_status,
        },
        "average_feature_psi": round(avg_feat_psi, 4),
        "features_monitored": num_features,
        "feature_drifts": feature_drift_results,
        "recommendation": recommendation,
        "requires_retraining_review": (overall_status == "DRIFT_DETECTED")
    }
