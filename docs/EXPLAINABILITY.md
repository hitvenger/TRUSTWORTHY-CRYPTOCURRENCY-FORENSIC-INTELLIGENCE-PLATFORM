# Forensic Explainability (XAI) & SHAP Integration

## 1. Case-Specific vs. Global Explanations
In digital forensics, global feature importance (e.g. general dataset Gini importance) is legally insufficient to justify why a *specific* transaction was flagged. TCF-FX computes **local transaction-bound SHAP values** ($TreeExplainer$) for every scored sample.

---

## 2. Decision Driver Decomposition
For every flagged lead, the platform outputs:
- **Base Expected Value**: The background dataset prior probability $E[f(x)]$.
- **Positive Drivers**: Specific features pushing the score upward toward high risk (e.g. high velocity bursts, rapid downstream drain).
- **Negative Drivers**: Features mitigating risk (e.g. mature wallet age, high counterparty diversity).
- **Evidence Binding**: Explanations are cryptographically bound to the specific evidence ID, feature schema version, and model version.
