"""
Unit Tests for Multi-Signal Risk Fusion, Uncertainty Bounds, and Corroboration Engine.
"""

import pytest
from forensic_engine.risk_engine import compute_forensic_risk
from forensic_engine.corroboration import evaluate_corroboration
from forensic_engine.uncertainty import compute_uncertainty_metrics


def test_corroboration_signal_evaluation():
    # Features showing high velocity and rapid drain
    suspicious_features = {
        "src_tx_velocity_hourly": 25.0,
        "src_past_1h_txs": 15.0,
        "rapid_drain_indicator": 1.0,
        "k_hop_suspicious_exposure": 0.5,
        "src_is_dormant_reactivation": 1.0,
        "src_out_degree": 18.0,
        "src_in_degree": 2.0,
    }

    corrob = evaluate_corroboration(
        features=suspicious_features,
        model_risk=0.85,
        anomaly_score=0.75
    )

    assert corrob["status"] in ["MODERATE", "STRONG"]
    assert corrob["supporting_indicator_count"] >= 3
    assert corrob["score"] > 0.5


def test_forensic_risk_fusion_and_priority_mapping():
    features = {
        "src_tx_velocity_hourly": 20.0,
        "rapid_drain_indicator": 1.0,
        "k_hop_suspicious_exposure": 0.4,
        "src_clustering_coefficient": 0.3
    }

    risk_profile = compute_forensic_risk(
        rf_risk=0.88,
        anomaly_score=0.72,
        features=features,
        evidence_verified=True,
        has_provenance=True
    )

    assert risk_profile["risk_level"] in ["HIGH", "CRITICAL"]
    assert risk_profile["investigative_priority"] in [1, 2]
    assert "uncertainty" in risk_profile
    assert "subscores" in risk_profile
    assert risk_profile["subscores"]["rf_risk"] == 0.88
    assert risk_profile["subscores"]["anomaly_score"] == 0.72


def test_uncertainty_metrics_structure():
    unc = compute_uncertainty_metrics(
        model_prob=0.91,
        tree_predictions=[0.90, 0.92, 0.91, 0.89, 0.93],
        evidence_verified=True,
        has_provenance=True,
        corroboration_score=0.8
    )

    assert unc["model_probability"] == 0.91
    assert unc["model_confidence_level"] == "HIGH"
    assert unc["evidence_quality"] == "HIGH"
    assert unc["prediction_stability"] == "HIGH"
    assert 0.0 < unc["uncertainty_delta"] < 0.20
