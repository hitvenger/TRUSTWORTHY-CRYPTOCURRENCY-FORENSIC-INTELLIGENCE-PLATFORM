"""
Unit Tests for SHAP Explainability Engine and Evidence Attribution Binding.
"""

import pytest
import numpy as np
from forensic_engine.ml.random_forest import ForensicRandomForest
from forensic_engine.explainability.shap_engine import ForensicShapExplainer
from forensic_engine.ml.pipeline import FEATURE_COLUMNS


def test_shap_explanation_generation_and_binding():
    # Synthetic small dataset
    X_train = np.random.randn(50, len(FEATURE_COLUMNS))
    y_train = np.random.randint(0, 2, size=50)

    rf = ForensicRandomForest(n_estimators=30, max_depth=5, random_state=42)
    rf.fit(X_train, y_train, feature_names=FEATURE_COLUMNS)

    explainer = ForensicShapExplainer(
        model=rf,
        feature_names=FEATURE_COLUMNS,
        background_data=X_train[:20]
    )

    sample_x = X_train[0]
    explanation = explainer.explain_instance(
        X_sample=sample_x,
        transaction_id="tx_test_shap",
        evidence_id="ev_test_shap",
        model_version="1.0.0",
        risk_score=0.88,
        top_k=5
    )

    assert explanation["transaction_id"] == "tx_test_shap"
    assert explanation["evidence_id"] == "ev_test_shap"
    assert explanation["output_risk_score"] == 0.88
    assert "top_positive_contributors" in explanation
    assert "top_negative_contributors" in explanation
    assert "all_feature_attributions" in explanation
    assert len(explanation["top_positive_contributors"]) <= 5
    assert len(explanation["summary_drivers"]) > 0
