"""
End-to-End Forensic ML Evaluation Pipeline for TCF-FX.

Enforces:
1. Strict chronological temporal split (70% train / 30% test)
2. No temporal leakage in feature computation
3. Multi-model empirical evaluation with exact forensic metrics
"""

import time
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Tuple, Optional
from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    average_precision_score,
    confusion_matrix,
    brier_score_loss,
)

from forensic_engine.temporal_graph import IncrementalTemporalGraph
from forensic_engine.ml.random_forest import ForensicRandomForest
from forensic_engine.ml.isolation_forest import ForensicIsolationForest
from forensic_engine.ml.xgboost_model import ForensicGradientBoosting
from forensic_engine.ml.gnn_model import ForensicGraphSAGE


FEATURE_COLUMNS = [
    "amount",
    "log_amount",
    "src_in_degree",
    "src_out_degree",
    "src_total_degree",
    "src_unique_counterparties",
    "src_counterparty_diversity",
    "src_out_mean",
    "src_out_max",
    "src_out_std",
    "src_in_mean",
    "src_net_flow",
    "src_wallet_age_seconds",
    "src_time_since_last_tx",
    "src_tx_velocity_hourly",
    "src_is_dormant_reactivation",
    "src_past_1h_txs",
    "src_past_1h_vol",
    "src_past_24h_txs",
    "src_past_24h_vol",
    "dst_in_degree",
    "dst_out_degree",
    "dst_total_degree",
    "dst_unique_counterparties",
    "dst_in_mean",
    "dst_wallet_age_seconds",
    "src_clustering_coefficient",
    "src_1hop_neighborhood_size",
    "k_hop_suspicious_exposure",
    "rapid_drain_indicator",
]


def extract_features_and_split(
    transactions: List[Dict[str, Any]],
    train_ratio: float = 0.70
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, List[str], List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Processes transaction stream incrementally and performs chronological temporal split.
    """
    # 1. Sort strictly chronologically
    sorted_txs = sorted(transactions, key=lambda x: float(x.get("timestamp", 0.0)))
    
    # 2. Extract features using leak-proof temporal graph
    graph_engine = IncrementalTemporalGraph()
    enriched = graph_engine.process_transaction_stream(sorted_txs)

    # 3. Build matrix
    X_list = []
    y_list = []
    for tx in enriched:
        feats = tx["features"]
        row = [feats.get(col, 0.0) for col in FEATURE_COLUMNS]
        X_list.append(row)
        y_list.append(int(tx.get("label", 0)))

    X = np.array(X_list, dtype=np.float32)
    y = np.array(y_list, dtype=np.int32)

    # 4. Temporal split
    split_idx = int(len(X) * train_ratio)
    X_train, X_test = X[:split_idx], X[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]
    train_txs, test_txs = enriched[:split_idx], enriched[split_idx:]

    return X_train, y_train, X_test, y_test, FEATURE_COLUMNS, train_txs, test_txs


def evaluate_model_performance(
    model: Any,
    X_test: np.ndarray,
    y_test: np.ndarray,
    model_name: str,
    threshold: float = 0.50
) -> Dict[str, Any]:
    """
    Computes rigorous forensic evaluation metrics.
    """
    start_time = time.perf_counter()
    if hasattr(model, "predict_risk"):
        y_scores = model.predict_risk(X_test)
    elif hasattr(model, "predict_anomaly_score"):
        y_scores = model.predict_anomaly_score(X_test)
    else:
        probs = model.predict_proba(X_test)
        y_scores = probs[:, 1]
    
    latency_total_ms = (time.perf_counter() - start_time) * 1000.0
    latency_per_sample_ms = latency_total_ms / max(1, len(X_test))

    y_pred = (y_scores >= threshold).astype(int)

    # Compute metrics
    prec = float(precision_score(y_test, y_pred, zero_division=0))
    rec = float(recall_score(y_test, y_pred, zero_division=0))
    f1 = float(f1_score(y_test, y_pred, zero_division=0))
    
    try:
        roc_auc = float(roc_auc_score(y_test, y_scores))
    except Exception:
        roc_auc = 0.5

    try:
        pr_auc = float(average_precision_score(y_test, y_scores))
    except Exception:
        pr_auc = 0.0

    brier = float(brier_score_loss(y_test, y_scores))

    cm = confusion_matrix(y_test, y_pred)
    if cm.shape == (2, 2):
        tn, fp, fn, tp = cm.ravel()
    else:
        tn, fp, fn, tp = 0, 0, 0, 0
        if len(y_test) > 0 and y_test[0] == 0:
            tn = int(len(y_test))
        else:
            tp = int(len(y_test))

    fpr = float(fp / max(1, fp + tn))
    fnr = float(fn / max(1, fn + tp))

    return {
        "model_name": model_name,
        "sample_count": len(y_test),
        "precision": round(prec, 4),
        "recall": round(rec, 4),
        "f1": round(f1, 4),
        "roc_auc": round(roc_auc, 4),
        "pr_auc": round(pr_auc, 4),
        "brier_score": round(brier, 4),
        "confusion_matrix": {
            "true_positives": int(tp),
            "false_positives": int(fp),
            "true_negatives": int(tn),
            "false_negatives": int(fn),
            "false_positive_rate": round(fpr, 4),
            "false_negative_rate": round(fnr, 4),
        },
        "latency_per_sample_ms": round(latency_per_sample_ms, 3),
        "inference_scores": y_scores,
    }
