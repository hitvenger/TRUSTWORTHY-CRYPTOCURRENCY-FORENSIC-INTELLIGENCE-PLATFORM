"""
Abstract Base Forensic Classifier Interface for TCF-FX.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import numpy as np
import joblib


class BaseForensicModel(ABC):
    def __init__(self, model_id: str, version: str):
        self.model_id = model_id
        self.version = version
        self.is_trained = False
        self.feature_names: List[str] = []

    @abstractmethod
    def fit(self, X: np.ndarray, y: np.ndarray, feature_names: Optional[List[str]] = None) -> Any:
        pass

    @abstractmethod
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        pass

    def save(self, filepath: str):
        joblib.dump({
            "model_id": self.model_id,
            "version": self.version,
            "is_trained": self.is_trained,
            "feature_names": self.feature_names,
            "model_state": self._get_serializable_state()
        }, filepath)

    def load(self, filepath: str):
        data = joblib.load(filepath)
        self.model_id = data["model_id"]
        self.version = data["version"]
        self.is_trained = data["is_trained"]
        self.feature_names = data["feature_names"]
        self._load_serializable_state(data["model_state"])

    @abstractmethod
    def _get_serializable_state(self) -> Any:
        pass

    @abstractmethod
    def _load_serializable_state(self, state: Any):
        pass
