"""
Forensic Gradient Boosting (XGBoost) Classifier for TCF-FX.

Provides modern gradient boosted decision tree comparison against Random Forest.
Includes seamless fallback to scikit-learn GradientBoostingClassifier if native XGBoost is initializing.
"""

import numpy as np
from typing import Dict, Any, List, Optional
from forensic_engine.ml.base import BaseForensicModel

try:
    import xgboost as xgb
    HAS_NATIVE_XGB = True
except ImportError:
    HAS_NATIVE_XGB = False
    from sklearn.ensemble import HistGradientBoostingClassifier


class ForensicGradientBoosting(BaseForensicModel):
    def __init__(
        self,
        n_estimators: int = 200,
        max_depth: int = 6,
        learning_rate: float = 0.05,
        random_state: int = 42,
        model_id: str = "model_xgboost_tabular",
        version: str = "1.0.0"
    ):
        super().__init__(model_id=model_id, version=version)
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.learning_rate = learning_rate
        self.random_state = random_state
        self.is_native = HAS_NATIVE_XGB

        if self.is_native:
            self.clf = xgb.XGBClassifier(
                n_estimators=self.n_estimators,
                max_depth=self.max_depth,
                learning_rate=self.learning_rate,
                random_state=self.random_state,
                eval_metric="logloss",
                use_label_encoder=False,
                n_jobs=-1
            )
        else:
            self.clf = HistGradientBoostingClassifier(
                max_iter=self.n_estimators,
                max_depth=self.max_depth,
                learning_rate=self.learning_rate,
                random_state=self.random_state
            )

    def fit(self, X: np.ndarray, y: np.ndarray, feature_names: Optional[List[str]] = None) -> "ForensicGradientBoosting":
        self.clf.fit(X, y)
        self.is_trained = True
        if feature_names:
            self.feature_names = list(feature_names)
        return self

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        if not self.is_trained:
            raise RuntimeError("Model must be trained before calling predict_proba.")
        return self.clf.predict_proba(X)

    def predict_risk(self, X: np.ndarray) -> np.ndarray:
        probs = self.predict_proba(X)
        return probs[:, 1]

    def _get_serializable_state(self) -> Any:
        return {"clf": self.clf, "is_native": self.is_native}

    def _load_serializable_state(self, state: Any):
        self.clf = state["clf"]
        self.is_native = state["is_native"]
