# System Architecture & Technical Specification

## 1. System Philosophy & High-Level Architecture
TCF-FX is architected as a modular, decoupled digital forensics intelligence platform. The domain logic within `forensic_engine/` is completely standalone, ensuring mathematical determinism, zero side-effects, and headless script/CLI execution without requiring a web backend or graphical interface.

```
+---------------------------------------------------------------------------------------+
|                                    TCF-FX Web UI                                      |
|            (React 18 + TypeScript + Tailwind CSS + Lucide Icons + Vite)               |
+-------------------------------------------+-------------------------------------------+
                                            | REST API (FastAPI v1)
                                            v
+---------------------------------------------------------------------------------------+
|                                  TCF-FX Core Backend                                  |
|         - Auth & RBAC Middleware          - Report Generator (PDF, JSON, CSV)         |
|         - Case Management Service         - Audit & Chained Custody Logger            |
|         - Evidence Ingestion Pipeline     - Model Registry & Drift Monitor            |
+-------------------------------------------+-------------------------------------------+
                                            |
                  +-------------------------+-------------------------+
                  v                                                   v
+-------------------------------------------+       +-----------------------------------+
|              Forensic Engine              |       |         Blockchain Anchor         |
| - Deterministic Canonical Serialization   |       | - EvidenceAnchor.sol Contract     |
| - SHA-256 Digest Generator & Verifier     |       | - Web3 / Simulated EVM Client     |
| - Incremental Temporal Graph Engine       |       | - Off-chain privacy preservation  |
| - Paper Baseline Random Forest (250 trees)|       +-----------------------------------+
| - Isolation Forest Anomaly Ranker         |
| - SHAP Local TreeExplainer Attributions   |
| - Forensic Risk & Uncertainty Fusion      |
| - Multi-Signal Corroboration Engine       |
| - Population Stability Index (PSI) Drift  |
+-------------------------------------------+
```

---

## 2. Component Decoupling
1. **`forensic_engine/canonical.py`**: Pure Python deterministic normalization guaranteeing exact byte-level repeatability across operating systems and architectures.
2. **`forensic_engine/hashing.py`**: SHA-256 hashing and field-level tamper localization.
3. **`forensic_engine/custody.py`**: Cryptographic hash chain implementation linking consecutive events.
4. **`forensic_engine/temporal_graph.py`**: Stateful incremental graph builder maintaining strict chronological invariants $G(t-)$.
5. **`forensic_engine/ml/`**: Model implementations (Random Forest, Isolation Forest, XGBoost, GraphSAGE).
6. **`backend/app/`**: Enterprise-grade FastAPI application with SQLAlchemy ORM, Pydantic schemas, and JWT authentication.
7. **`frontend/`**: SOC laboratory dark-mode dashboard with real-time graph visualization.
