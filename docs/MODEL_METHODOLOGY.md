# Machine Learning Methodology & Temporal Anti-Leakage

## 1. Paper Baseline Model Specification
The primary supervised model faithfully reproduces the paper's reference baseline:
```python
RandomForestClassifier(
    n_estimators=250,
    max_depth=12,
    class_weight="balanced",
    random_state=42,
    n_jobs=-1
)
```

---

## 2. Temporal Anti-Leakage Guarantee

### The Mathematical Problem
Standard tabular machine learning pipelines frequently shuffle datasets or compute graph centralities over the complete dataset prior to train/test partitioning. In blockchain forensics, this creates fatal **future graph leakage**, where historical transactions incorporate future topological information that was unknowable at timestamp $t$.

### The TCF-FX Solution
1. Ingest transactions in strict chronological order: $t_1 \le t_2 \le \dots \le t_N$.
2. For transaction $tx_i$ at time $t_i$:
   - Extract features strictly from historical graph state $G(t_i^-)$.
   - Perform model scoring and SHAP explanation.
   - Only after feature extraction is complete, update the graph to state $G(t_i)$.
3. Partition datasets strictly by chronological time horizon (70% train / 30% test).
