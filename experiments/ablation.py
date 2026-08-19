"""
Forensic Ablation Study Framework for TCF-FX.

Evaluates 7 distinct analytical configurations:
A — RF Baseline Only (amount + raw degree)
B — RF + Graph Topological Features
C — RF + Temporal Velocity & Burst Features
D — RF + Unsupervised Anomaly Scoring
E — RF + Graph + Anomaly
F — GraphSAGE Relational Model
G — Full TCF-FX Fusion (RF + Graph + Temporal + Anomaly + Corroboration)
"""

import numpy as np
from typing import Dict, List, Any
from forensic_engine.ml.pipeline import extract_features_and_split, evaluate_model_performance, FEATURE_COLUMNS
from forensic_engine.ml.random_forest import ForensicRandomForest
from forensic_engine.ml.isolation_forest import ForensicIsolationForest
from forensic_engine.ml.gnn_model import ForensicGraphSAGE
from forensic_engine.risk_engine import compute_forensic_risk


def run_ablation_study(transactions: List[Dict[str, Any]], seed: int = 42) -> Dict[str, Any]:
    """Executes the complete 7-part ablation matrix."""
    X_train, y_train, X_test, y_test, feat_cols, train_txs, test_txs = extract_features_and_split(
        transactions, train_ratio=0.70
    )

    # Feature index masks:
    # Basic tabular: amount, log_amount (0, 1)
    # Graph features: degrees, counterparties, clustering, neighborhood, k-hop (2-6, 20-23, 26-28)
    # Temporal features: velocity, age, bursts, rapid drain (12-19, 24-25, 29)
    
    idx_amount = [0, 1]
    idx_graph = [2, 3, 4, 5, 6, 20, 21, 22, 23, 26, 27, 28]
    idx_temporal = [12, 13, 14, 15, 16, 17, 18, 19, 24, 25, 29]
    idx_all_features = list(range(len(feat_cols)))

    results = []

    # Config A: RF Basic
    rf_a = ForensicRandomForest(random_state=seed)
    cols_a = idx_amount + [2, 3]  # amount + basic in/out degree
    rf_a.fit(X_train[:, cols_a], y_train)
    res_a = evaluate_model_performance(rf_a, X_test[:, cols_a], y_test, "A: RF Baseline (Basic)")
    res_a["config_description"] = "Random Forest with basic transaction amount and unweighted degrees only"
    results.append(res_a)

    # Config B: RF + Graph
    rf_b = ForensicRandomForest(random_state=seed)
    cols_b = idx_amount + idx_graph
    rf_b.fit(X_train[:, cols_b], y_train)
    res_b = evaluate_model_performance(rf_b, X_test[:, cols_b], y_test, "B: RF + Graph Topology")
    res_b["config_description"] = "RF with amount + full topological clustering, k-hop exposure, and counterparty diversity"
    results.append(res_b)

    # Config C: RF + Temporal
    rf_c = ForensicRandomForest(random_state=seed)
    cols_c = idx_amount + idx_temporal
    rf_c.fit(X_train[:, cols_c], y_train)
    res_c = evaluate_model_performance(rf_c, X_test[:, cols_c], y_test, "C: RF + Temporal Dynamics")
    res_c["config_description"] = "RF with amount + velocity bursts, dormancy transitions, and rolling 1h/24h metrics"
    results.append(res_c)

    # Config D: RF + Anomaly
    iforest = ForensicIsolationForest(random_state=seed)
    iforest.fit(X_train[:, idx_all_features])
    anom_train = iforest.predict_anomaly_score(X_train[:, idx_all_features]).reshape(-1, 1)
    anom_test = iforest.predict_anomaly_score(X_test[:, idx_all_features]).reshape(-1, 1)
    
    rf_d = ForensicRandomForest(random_state=seed)
    X_tr_d = np.hstack([X_train[:, idx_amount], anom_train])
    X_te_d = np.hstack([X_test[:, idx_amount], anom_test])
    rf_d.fit(X_tr_d, y_train)
    res_d = evaluate_model_performance(rf_d, X_te_d, y_test, "D: RF + Isolation Forest Anomaly")
    res_d["config_description"] = "RF with amount + unsupervised Isolation Forest anomaly features"
    results.append(res_d)

    # Config E: RF + Graph + Anomaly
    rf_e = ForensicRandomForest(random_state=seed)
    X_tr_e = np.hstack([X_train[:, cols_b], anom_train])
    X_te_e = np.hstack([X_test[:, cols_b], anom_test])
    rf_e.fit(X_tr_e, y_train)
    res_e = evaluate_model_performance(rf_e, X_te_e, y_test, "E: RF + Graph + Anomaly")
    res_e["config_description"] = "RF with graph features and unsupervised anomaly detection"
    results.append(res_e)

    # Config F: GraphSAGE Relational
    gs = ForensicGraphSAGE(in_dim=len(idx_all_features), random_state=seed)
    gs.fit(X_train, y_train)
    res_f = evaluate_model_performance(gs, X_test, y_test, "F: GraphSAGE Relational")
    res_f["config_description"] = "Inductive GraphSAGE neural network modeling neighborhood aggregation"
    results.append(res_f)

    # Config G: Full TCF-FX Fusion
    rf_full = ForensicRandomForest(random_state=seed)
    rf_full.fit(X_train, y_train)
    rf_scores = rf_full.predict_risk(X_test)
    anom_scores = iforest.predict_anomaly_score(X_test)
    
    fusion_scores = []
    for idx, tx in enumerate(test_txs):
        fused = compute_forensic_risk(
            rf_risk=rf_scores[idx],
            anomaly_score=anom_scores[idx],
            features=tx["features"]
        )
        fusion_scores.append(fused["overall_risk"])
        
    fusion_scores_arr = np.array(fusion_scores)
    
    # Evaluate fusion
    class DummyFusionModel:
        def predict_risk(self, X):
            return fusion_scores_arr

    res_g = evaluate_model_performance(DummyFusionModel(), X_test, y_test, "G: Full TCF-FX Multi-Signal Fusion")
    res_g["config_description"] = "Full pipeline: RF + Graph + Temporal + Isolation Forest + Multi-Signal Corroboration"
    results.append(res_g)

    # Clean inference scores out of summary table for clean JSON serialization
    summary_table = []
    for r in results:
        summary_table.append({
            "model_name": r["model_name"],
            "config_description": r["config_description"],
            "precision": r["precision"],
            "recall": r["recall"],
            "f1": r["f1"],
            "roc_auc": r["roc_auc"],
            "pr_auc": r["pr_auc"],
            "brier_score": r["brier_score"],
            "latency_per_sample_ms": r["latency_per_sample_ms"],
        })

    return {
        "ablation_summary": summary_table,
        "detailed_results": results,
    }
