"""
Elliptic Bitcoin Dataset Adapter for TCF-FX.

Provides a clean forensic adapter for loading and partitioning the public Elliptic CSV triplet:
1. elliptic_txs_features.csv (node features and time steps)
2. elliptic_txs_classes.csv (labels: 1=illicit, 2=licit, unknown)
3. elliptic_txs_edgelist.csv (directed transaction graph edges)

NOTE: This adapter respects licensing and does not bundle proprietary dataset files.
It validates local presence and executes chronological transformations.
"""

import os
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple


class EllipticDatasetAdapter:
    def __init__(self, data_directory: str = "datasets/elliptic"):
        self.data_dir = data_directory
        self.features_file = os.path.join(data_directory, "elliptic_txs_features.csv")
        self.classes_file = os.path.join(data_directory, "elliptic_txs_classes.csv")
        self.edgelist_file = os.path.join(data_directory, "elliptic_txs_edgelist.csv")

    def check_availability(self) -> Dict[str, Any]:
        """Checks whether the expected Elliptic CSV triplet exists locally."""
        features_exists = os.path.exists(self.features_file)
        classes_exists = os.path.exists(self.classes_file)
        edgelist_exists = os.path.exists(self.edgelist_file)
        
        all_present = features_exists and classes_exists and edgelist_exists
        
        return {
            "available": all_present,
            "status": "DATA_PRESENT" if all_present else "DATA_REQUIRED",
            "directory": os.path.abspath(self.data_dir),
            "files": {
                "features": {"path": self.features_file, "exists": features_exists},
                "classes": {"path": self.classes_file, "exists": classes_exists},
                "edgelist": {"path": self.edgelist_file, "exists": edgelist_exists},
            },
            "instructions": (
                "To evaluate on the real Elliptic Bitcoin dataset, download the triplet from Kaggle / official repository "
                f"and place the three CSV files in: {os.path.abspath(self.data_dir)}"
            ) if not all_present else "Dataset files verified."
        }

    def load_and_preprocess(
        self,
        max_timesteps: Optional[int] = None,
        filter_unknown: bool = True
    ) -> Dict[str, Any]:
        """
        Loads the Elliptic dataset, preserves chronological ordering, and maps labels.
        Classes mapping: '1' -> 1 (illicit), '2' -> 0 (licit), 'unknown' -> -1.
        """
        status = self.check_availability()
        if not status["available"]:
            raise FileNotFoundError(
                f"Elliptic dataset files missing in {self.data_dir}. {status['instructions']}"
            )

        # Load classes
        df_classes = pd.read_csv(self.classes_file)
        # Load features (no header: col 0 is txId, col 1 is time_step, remaining are 165 features)
        df_features = pd.read_csv(self.features_file, header=None)
        df_features.rename(columns={0: "txId", 1: "time_step"}, inplace=True)

        # Merge
        merged = pd.merge(df_features, df_classes, on="txId")

        if filter_unknown:
            merged = merged[merged["class"].isin(["1", "2", 1, 2])].copy()

        merged["label"] = merged["class"].apply(lambda x: 1 if str(x) == "1" else 0)

        # Sort chronologically by time_step
        merged = merged.sort_values(by=["time_step", "txId"]).reset_index(drop=True)

        if max_timesteps:
            merged = merged[merged["time_step"] <= max_timesteps].copy()

        # Load edgelist
        df_edges = pd.read_csv(self.edgelist_file)

        return {
            "dataframe": merged,
            "edges": df_edges,
            "total_nodes": len(merged),
            "illicit_count": int(sum(merged["label"] == 1)),
            "licit_count": int(sum(merged["label"] == 0)),
            "time_steps": int(merged["time_step"].nunique()),
        }
