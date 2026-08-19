"""
Forensic Isolation Forest Anomaly Detection Engine for TCF-FX.

Provides unsupervised topological and feature anomaly detection.
Crucial Rule: Anomaly scores are NOT probabilities; they quantify distance
from normal background cryptocurrency transaction manifolds.
"""

import numpy as np
from sklearn.ensemble import IsolationForest
from typing import Dict, Any, List, Optional
from forensic_engine.ml.base import BaseForensicModel


class ForensicIsolationForest(BaseForensicModel):
    def __init__(
        self,
        n_estimators: int = 150,
        contamination: float = 0.08,
        random_state: int = 42,
        model_id: str = "model_iforest_unsupervised",
        version: str = "1.0.0"
    ):
        super().__init__(model_id=model_id, version=version)
        self.n_estimators = n_estimators
        self.contamination = contamination
        self.random_state = random_state
        self.clf = IsolationForest(
            n_estimators=self.n_estimators,
            contamination=self.contamination,
            random_state=self.random_state,
            n_jobs=-1
        )
        self.baseline_score_quantiles = []

    def fit(self, X: np.ndarray, y: Optional[np.ndarray] = None, feature_names: Optional[List[str]] = None) -> "ForensicIsolationForest":
        self.clf.fit(X)
        self.is_trained = True
        if feature_names:
            self.feature_names = list(feature_names)
            
        # Calibrate score quantiles on training data
        raw_scores = self.clf.decision_function(X)
        # Decision function: lower values mean more anomalous
        # Transform to anomaly scores where higher = more anomalous
        inverted = -raw_scores
        self.baseline_score_quantiles = list(np.percentile(inverted, np.linspace(0, 100, 101)))
        return self

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """
        Mock proba interface for BaseForensicModel compatibility.
        Returns normalized anomaly scores.
        """
        scores = self.predict_anomaly_score(X)
        return np.column_stack([1.0 - scores, scores])

    def predict_anomaly_score(self, X: np.ndarray) -> np.ndarray:
        """
        Computes calibrated anomaly score in range [0.0, 1.0].
        0.0 = completely normal / routine manifold.
        1.0 = extreme outlier / abnormal behavior.
        """
        if not self.is_trained:
            raise RuntimeError("Model must be trained before predicting anomaly scores.")
        
        raw = self.clf.decision_function(X)
        # Invert: raw < 0 is anomalous, raw > 0 is normal
        # Sigmoid / Min-Max normalization against empirical decision function range
        # Typically raw is in [-0.5, 0.5]
        normalized = 1.0 / (1.0 + np.exp(raw * 8.0))
        return np.clip(normalized, 0.0, 1.0)

    def analyze_anomaly(self, X_single: np.ndarray, threshold: float = 0.65) -> Dict[str, Any]:
        """
        Produces detailed anomaly diagnostics for a single transaction sample.
        """
        if X_single.ndim == 1:
            X_single = X_single.reshape(1, -1)
            
        score = float(self.predict_anomaly_score(X_single)[0])
        is_anomalous = bool(score >= threshold)
        
        # Calculate empirical percentile rank
        inverted = -float(self.clf.decision_function(X_single)[0])
        if self.baseline_score_quantiles:
            rank_pct = float(np.searchsorted(self.baseline_score_quantiles, inverted) / len(self.baseline_score_quantiles))
        else:
            rank_pct = score

        return {
            "anomaly_score": round(score, 4),
            "is_anomalous": is_anomalous,
            "anomaly_rank_percentile": round(rank_pct * 100.0, 2),
            "anomaly_severity": "CRITICAL" if score >= 0.85 else ("HIGH" if score >= 0.65 else ("MODERATE" if score >= 0.40 else "LOW")),
            "note": "Isolation Forest anomaly score indicates statistical deviation from regular transaction topologies."
        }

    def _get_serializable_state(self) -> Any:
        return {"clf": self.clf, "quantiles": self.baseline_score_quantiles}

    def _load_serializable_state(self, state: Any):
        self.clf = state["clf"]
        self.baseline_score_quantiles = state["quantiles"]
