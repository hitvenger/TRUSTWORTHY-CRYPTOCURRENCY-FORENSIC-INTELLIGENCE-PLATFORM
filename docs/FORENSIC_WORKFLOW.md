# Forensic Investigation Workflow

## 1. The 8-Stage Forensic Lifecycle

TCF-FX strictly implements the end-to-end digital forensics investigation lifecycle established in the foundational paper:

```
[1. Case Creation]
       │
       ▼
[2. Evidence Acquisition] ──► Ingest structured transaction telemetry
       │
       ▼
[3. Provenance Registration] ──► Capture origin, node ID, acquisition timestamp
       │
       ▼
[4. Evidence Preservation] ──► Deterministic Canonical JSON & SHA-256 Hashing
       │
       ▼
[5. Evidence Correlation] ──► Temporal Graph construction & topological mapping
       │
       ▼
[6. AI-Assisted Analysis] ──► Random Forest + Isolation Forest + XGBoost scoring
       │
       ▼
[7. Explanation & Review] ──► SHAP attributions & Mandatory Human Review
       │
       ▼
[8. Governance & Report] ──► Blockchain Anchor & Court-Ready PDF Dossier
```

---

## 2. Mandatory Principle: Human-in-the-Loop Triage

The analytical engine outputs an **Investigative Lead** (`MODEL_LEAD`).
An investigative lead is an algorithmic prioritization indicator.

### Promotion States:
1. `MODEL_LEAD`: Initial algorithm assessment.
2. `UNDER_REVIEW`: Assigned to human forensic analyst for secondary corroboration.
3. `FORENSIC_FINDING`: Formal finding promoted after analyst confirms topological corroboration.
4. `REJECTED`: Declared benign false positive with documented rationale.
5. `ESCALATED`: Escalated to senior investigative team for multi-jurisdiction tracing.
