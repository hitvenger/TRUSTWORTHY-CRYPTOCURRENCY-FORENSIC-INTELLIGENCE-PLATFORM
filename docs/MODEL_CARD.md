# Formal Model Cards & Governance

## 1. Reference Random Forest Baseline (`model_rf_baseline`)
- **Version**: 1.0.0
- **Model Type**: Supervised Ensemble of 250 Decision Trees
- **Intended Use**: Tabular transaction risk classification utilizing temporal graph features.
- **Prohibited Use**: Autonomous declaration of criminal fraud without qualified human review.
- **Training Partition**: Chronological 70% historical split with balanced class weighting.
- **Key Metrics**: F1: 0.884, ROC-AUC: 0.942, PR-AUC: 0.891, Brier Score: 0.052, Latency: 0.32 ms.

---

## 2. Unsupervised Isolation Forest (`model_iforest_unsupervised`)
- **Version**: 1.0.0
- **Model Type**: Unsupervised Tree Isolation Outlier Detector
- **Intended Use**: Statistical outlier scoring across multi-dimensional topological feature space.
- **Prohibited Use**: Labeling anomaly scores as legal probabilities of illicit conduct.
- **Contamination Parameter**: 0.08
- **Output**: Normalized Anomaly Score in $[0.0, 1.0]$ and empirical percentile ranking.
