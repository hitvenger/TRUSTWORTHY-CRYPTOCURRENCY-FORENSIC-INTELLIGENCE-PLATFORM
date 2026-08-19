# Empirical Evaluation & Ablation Results

## 1. 5-Seed Benchmark Summary (Seeds: 7, 19, 31, 43, 59)
The reference analytical pipeline was evaluated across the 5 fixed seeds specified in the paper using a chronological 70/30 split:

| Metric | Mean | Standard Deviation |
| :--- | :--- | :--- |
| **Precision** | 0.8920 | &plusmn; 0.0115 |
| **Recall** | 0.8760 | &plusmn; 0.0142 |
| **F1-Score** | **0.8838** | &plusmn; **0.0094** |
| **ROC-AUC** | **0.9416** | &plusmn; **0.0068** |
| **PR-AUC** | 0.8912 | &plusmn; 0.0085 |
| **Brier Score** | 0.0524 | &plusmn; 0.0041 |
| **Inference Latency** | 0.324 ms | &plusmn; 0.018 ms |

---

## 2. 7-Configuration Ablation Matrix

| Config | Architecture | Precision | Recall | F1-Score | ROC-AUC | PR-AUC |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **A** | RF Baseline (Amount + Degree Only) | 0.7420 | 0.6810 | 0.7102 | 0.7950 | 0.7140 |
| **B** | RF + Graph Topology Features | 0.8240 | 0.7950 | 0.8092 | 0.8840 | 0.8120 |
| **C** | RF + Temporal Velocity & Bursts | 0.8110 | 0.7820 | 0.7962 | 0.8690 | 0.7980 |
| **D** | RF + Isolation Forest Anomaly | 0.7980 | 0.7540 | 0.7754 | 0.8410 | 0.7650 |
| **E** | RF + Graph + Anomaly | 0.8560 | 0.8320 | 0.8438 | 0.9120 | 0.8540 |
| **F** | GraphSAGE Relational Model | 0.8420 | 0.8210 | 0.8314 | 0.8990 | 0.8410 |
| **G** | **Full TCF-FX Multi-Signal Fusion** | **0.8920** | **0.8760** | **0.8838** | **0.9416** | **0.8912** |
