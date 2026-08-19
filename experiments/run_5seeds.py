"""
Five-Seed Forensic Reproducibility Runner for TCF-FX.

Benchmarks the primary analytical pipeline across the 5 canonical seeds
specified in the foundational paper: (7, 19, 31, 43, 59).
Outputs mean ± standard deviation for all forensic metrics.
"""

import numpy as np
from typing import Dict, List, Any
from forensic_engine.ml.pipeline import extract_features_and_split, evaluate_model_performance
from forensic_engine.ml.random_forest import ForensicRandomForest
from forensic_engine.ml.isolation_forest import ForensicIsolationForest
from datasets.synthetic import generate_synthetic_dataset

FIXED_SEEDS = [7, 19, 31, 43, 59]


def run_5seed_reproducibility(
    num_samples: int = 3000,
    seeds: List[int] = FIXED_SEEDS
) -> Dict[str, Any]:
    """
    Executes multi-seed evaluation and computes statistical dispersion.
    """
    runs = []
    
    prec_list = []
    rec_list = []
    f1_list = []
    roc_list = []
    pr_list = []
    brier_list = []
    latency_list = []

    for s in seeds:
        # Generate dataset with seed
        txs = generate_synthetic_dataset(num_transactions=num_samples, seed=s)
        X_train, y_train, X_test, y_test, feat_cols, _, _ = extract_features_and_split(txs, train_ratio=0.70)
        
        # Train baseline RF
        rf = ForensicRandomForest(random_state=s)
        rf.fit(X_train, y_train, feature_names=feat_cols)
        
        eval_res = evaluate_model_performance(rf, X_test, y_test, f"RF (Seed {s})")
        
        runs.append({
            "seed": s,
            "precision": eval_res["precision"],
            "recall": eval_res["recall"],
            "f1": eval_res["f1"],
            "roc_auc": eval_res["roc_auc"],
            "pr_auc": eval_res["pr_auc"],
            "brier_score": eval_res["brier_score"],
            "latency_per_sample_ms": eval_res["latency_per_sample_ms"],
            "confusion_matrix": eval_res["confusion_matrix"],
        })
        
        prec_list.append(eval_res["precision"])
        rec_list.append(eval_res["recall"])
        f1_list.append(eval_res["f1"])
        roc_list.append(eval_res["roc_auc"])
        pr_list.append(eval_res["pr_auc"])
        brier_list.append(eval_res["brier_score"])
        latency_list.append(eval_res["latency_per_sample_ms"])

    summary = {
        "seeds_evaluated": seeds,
        "metrics_summary": {
            "precision": {"mean": round(float(np.mean(prec_list)), 4), "std": round(float(np.std(prec_list)), 4)},
            "recall": {"mean": round(float(np.mean(rec_list)), 4), "std": round(float(np.std(rec_list)), 4)},
            "f1": {"mean": round(float(np.mean(f1_list)), 4), "std": round(float(np.std(f1_list)), 4)},
            "roc_auc": {"mean": round(float(np.mean(roc_list)), 4), "std": round(float(np.std(roc_list)), 4)},
            "pr_auc": {"mean": round(float(np.mean(pr_list)), 4), "std": round(float(np.std(pr_list)), 4)},
            "brier_score": {"mean": round(float(np.mean(brier_list)), 4), "std": round(float(np.std(brier_list)), 4)},
            "latency_ms": {"mean": round(float(np.mean(latency_list)), 3), "std": round(float(np.std(latency_list)), 3)},
        },
        "individual_runs": runs
    }

    return summary
