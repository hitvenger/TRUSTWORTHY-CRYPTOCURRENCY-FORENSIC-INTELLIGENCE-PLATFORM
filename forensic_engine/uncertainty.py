"""
Forensic Uncertainty & Confidence Quantification Engine for TCF-FX.

Strictly distinguishes between:
- model_probability (raw classification score)
- model_confidence (distance from decision boundary / ensemble consensus)
- prediction_stability (estimator variance across ensemble trees)
- uncertainty (error bounds ± delta)
- evidence_quality (provenance, completeness, cryptographic integrity)
- forensic_confidence (integrated credibility index)
"""

import numpy as np
from typing import Dict, Any, List, Optional


def calculate_tree_variance(estimator_predictions: List[float]) -> float:
    """Calculates standard deviation across ensemble tree probability estimates."""
    if not estimator_predictions or len(estimator_predictions) < 2:
        return 0.05
    return float(np.std(estimator_predictions))


def compute_uncertainty_metrics(
    model_prob: float,
    tree_predictions: Optional[List[float]] = None,
    anomaly_score: float = 0.0,
    evidence_verified: bool = True,
    has_provenance: bool = True,
    corroboration_score: float = 0.5,
) -> Dict[str, Any]:
    """
    Computes rigorous uncertainty and multi-dimensional confidence breakdown.
    """
    prob = float(np.clip(model_prob, 0.0, 1.0))
    
    # 1. Prediction stability via ensemble tree variance
    if tree_predictions and len(tree_predictions) > 1:
        tree_std = float(np.std(tree_predictions))
    else:
        # Theoretical standard error heuristic based on Bernoulli variance
        tree_std = float(np.sqrt(max(1e-5, prob * (1.0 - prob)) / 250.0))
    
    # 2. Epistemic uncertainty margin (+- delta at 95% confidence approx 1.96 * std)
    uncertainty_margin = float(np.clip(1.96 * tree_std, 0.01, 0.25))
    
    # 3. Model boundary confidence (0 at 0.5, 1 at 0 or 1)
    boundary_distance = abs(prob - 0.5) * 2.0
    
    if boundary_distance >= 0.7 and tree_std <= 0.08:
        model_confidence_level = "HIGH"
    elif boundary_distance >= 0.3 and tree_std <= 0.15:
        model_confidence_level = "MEDIUM"
    else:
        model_confidence_level = "LOW"
        
    stability_level = "HIGH" if tree_std < 0.06 else ("MEDIUM" if tree_std < 0.12 else "LOW")
    
    # 4. Evidence Quality assessment
    eq_score = 1.0
    if not evidence_verified:
        eq_score -= 0.5
    if not has_provenance:
        eq_score -= 0.3
    eq_score = max(0.1, eq_score)
    
    if eq_score >= 0.9:
        evidence_quality = "HIGH"
    elif eq_score >= 0.6:
        evidence_quality = "MEDIUM"
    else:
        evidence_quality = "LOW"
        
    # 5. Composite Forensic Confidence (Model certainty weighted by corroboration and evidence integrity)
    forensic_confidence = (boundary_distance * 0.45) + (corroboration_score * 0.35) + (eq_score * 0.20)
    forensic_confidence = float(np.clip(forensic_confidence, 0.05, 0.99))
    
    return {
        "model_probability": round(prob, 4),
        "uncertainty_delta": round(uncertainty_margin, 4),
        "model_confidence_level": model_confidence_level,
        "prediction_stability": stability_level,
        "tree_std_error": round(tree_std, 4),
        "evidence_quality": evidence_quality,
        "evidence_quality_score": round(eq_score, 2),
        "forensic_confidence": round(forensic_confidence, 4),
        "formatted_display": f"{round(prob, 2)} ± {round(uncertainty_margin, 2)} ({model_confidence_level} Confidence)"
    }
