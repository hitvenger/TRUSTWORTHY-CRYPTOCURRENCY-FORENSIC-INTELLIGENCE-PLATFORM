"""
Reference Baseline Random Forest Classifier for TCF-FX.

Directly implements the Paper Baseline specification:
RandomForestClassifier(
    n_estimators=250,
    max_depth=12,
    class_weight="balanced",
    random_state=42,
    n_jobs=-1
)
"""

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from typing import Dict, Any, List, Optional
from forensic_engine.ml.base import BaseForensicModel


class ForensicRandomForest(BaseForensicModel):
    def __init__(
        self,
        n_estimators: int = 250,
        max_depth: int = 12,
        class_weight: str = "balanced",
        random_state: int = 42,
        model_id: str = "model_rf_baseline",
        version: str = "1.0.0"
    ):
        super().__init__(model_id=model_id, version=version)
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.class_weight = class_weight
        self.random_state = random_state
        self.clf = RandomForestClassifier(
            n_estimators=self.n_estimators,
            max_depth=self.max_depth,
            class_weight=self.class_weight,
            random_state=self.random_state,
            n_jobs=-1
        )

    def fit(self, X: np.ndarray, y: np.ndarray, feature_names: Optional[List[str]] = None) -> "ForensicRandomForest":
        self.clf.fit(X, y)
        self.is_trained = True
        if feature_names:
            self.feature_names = list(feature_names)
        return self

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        if not self.is_trained:
            raise RuntimeError("Model must be trained before calling predict_proba.")
        probs = self.clf.predict_proba(X)
        if probs.shape[1] == 1:
            # Single class edge case
            return np.column_stack([1.0 - probs[:, 0], probs[:, 0]])
        return probs

    def predict_risk(self, X: np.ndarray) -> np.ndarray:
        """Returns risk probabilities for illicit/flagged class (class 1)."""
        probs = self.predict_proba(X)
        return probs[:, 1]

    def get_individual_tree_predictions(self, X_single: np.ndarray) -> List[float]:
        """
        Returns predictions from every individual tree estimator for a single sample.
        Used by the Uncertainty Engine to quantify ensemble disagreement.
        """
        if not self.is_trained:
            return [0.5]
        if X_single.ndim == 1:
            X_single = X_single.reshape(1, -1)
            
        tree_probs = []
        for estimator in self.clf.estimators_:
            p = estimator.predict_proba(X_single)
            tree_probs.append(float(p[0, 1] if p.shape[1] > 1 else p[0, 0]))
        return tree_probs

    def get_feature_importances(self) -> Dict[str, float]:
        if not self.is_trained:
            return {}
        importances = self.clf.feature_importances_
        names = self.feature_names or [f"f_{i}" for i in range(len(importances))]
        return {name: float(round(imp, 6)) for name, imp in sorted(zip(names, importances), key=lambda x: x[1], reverse=True)}

    def _get_serializable_state(self) -> Any:
        return self.clf

    def _load_serializable_state(self, state: Any):
        self.clf = state
