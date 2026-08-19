"""
Unit Tests for Machine Learning Models, Baseline Reproducibility, and Isolation Forest.
"""

import pytest
import numpy as np
from forensic_engine.ml.random_forest import ForensicRandomForest
from forensic_engine.ml.isolation_forest import ForensicIsolationForest
from forensic_engine.ml.xgboost_model import ForensicGradientBoosting
from datasets.synthetic import generate_synthetic_dataset
from forensic_engine.ml.pipeline import extract_features_and_split


@pytest.fixture
def synthetic_data():
    txs = generate_synthetic_dataset(num_transactions=800, seed=42)
    return extract_features_and_split(txs, train_ratio=0.70)


def test_random_forest_baseline_specification(synthetic_data):
    X_train, y_train, X_test, y_test, feat_cols, _, _ = synthetic_data
    rf = ForensicRandomForest(random_state=42)
    
    # Assert paper baseline parameters
    assert rf.n_estimators == 250
    assert rf.max_depth == 12
    assert rf.class_weight == "balanced"
    assert rf.random_state == 42

    rf.fit(X_train, y_train, feature_names=feat_cols)
    assert rf.is_trained is True

    probs = rf.predict_proba(X_test)
    assert probs.shape == (len(X_test), 2)
    assert np.all((probs >= 0.0) & (probs <= 1.0))

    # Test individual tree predictions for uncertainty estimation
    tree_preds = rf.get_individual_tree_predictions(X_test[0])
    assert len(tree_preds) == 250


def test_isolation_forest_anomaly_scoring(synthetic_data):
    X_train, _, X_test, _, feat_cols, _, _ = synthetic_data
    iforest = ForensicIsolationForest(random_state=42)
    iforest.fit(X_train, feature_names=feat_cols)

    anom_scores = iforest.predict_anomaly_score(X_test)
    assert len(anom_scores) == len(X_test)
    assert np.all((anom_scores >= 0.0) & (anom_scores <= 1.0))

    diag = iforest.analyze_anomaly(X_test[0])
    assert "anomaly_score" in diag
    assert "anomaly_rank_percentile" in diag
    assert "is_anomalous" in diag


def test_deterministic_training_reproducibility(synthetic_data):
    X_train, y_train, X_test, _, _, _, _ = synthetic_data
    rf1 = ForensicRandomForest(random_state=42).fit(X_train, y_train)
    rf2 = ForensicRandomForest(random_state=42).fit(X_train, y_train)

    preds1 = rf1.predict_risk(X_test)
    preds2 = rf2.predict_risk(X_test)

    assert np.allclose(preds1, preds2, atol=1e-7)
