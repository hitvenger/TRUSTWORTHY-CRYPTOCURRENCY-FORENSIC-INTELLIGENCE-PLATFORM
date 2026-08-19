# Forensic Uncertainty Quantification & Calibration

## 1. Distinction of Metrics
TCF-FX rigorously distinguishes between non-interchangeable statistical concepts:
1. **Model Probability ($p$)**: Raw ensemble output $p \in [0.0, 1.0]$.
2. **Model Confidence**: Boundary margin $|p - 0.5| \times 2.0$ weighted by tree agreement.
3. **Prediction Stability**: Variance across the 250 individual tree estimators $\sigma_{\text{trees}}$.
4. **Epistemic Uncertainty Margin ($\pm \delta$)**: 95% confidence standard error interval ($\approx 1.96 \cdot \sigma_{\text{trees}}$).
5. **Evidence Quality**: Provenance reliability and SHA-256 integrity status.
6. **Forensic Confidence**: Compound index synthesizing model certainty, corroboration count, and cryptographic verification.

The platform never displays misleading statements such as "91% certainty of guilt", but rather presents calibrated intervals: `0.91 ± 0.06 (HIGH Confidence)`.
