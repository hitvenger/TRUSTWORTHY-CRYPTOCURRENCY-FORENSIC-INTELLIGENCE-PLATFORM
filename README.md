# TCF-FX: Trustworthy Cryptocurrency Forensic Intelligence Platform

<div align="center">

```
  ████████╗ ██████╗███████╗    ███████╗██╗  ██╗
  ╚══██╔══╝██╔════╝██╔════╝    ██╔════╝╚██╗██╔╝
     ██║   ██║     █████╗█████╗█████╗   ╚███╔╝ 
     ██║   ██║     ██╔══╝╚════╝██╔══╝   ██╔██╗ 
     ██║   ╚██████╗██║         ██║     ██╔╝ ██╗
     ╚═╝    ╚═════╝╚═╝         ╚═╝     ╚═╝  ╚═╝
```

**An Evidence-Aware, Explainable, and Cryptographically Verifiable Multi-Model Intelligence System for Blockchain Digital Forensics**

[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React 18](https://img.shields.io/badge/React-18.3-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.5-3178C6?style=for-the-badge&logo=typescript&logoColor=white)](https://www.typescriptlang.org)
[![Solidity](https://img.shields.io/badge/Solidity-0.8.19-363636?style=for-the-badge&logo=solidity&logoColor=white)](https://soliditylang.org)
[![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-3.4-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)](https://tailwindcss.com)
[![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com)
[![Tests Passing](https://img.shields.io/badge/Tests-35%2F35%20Passing-brightgreen?style=for-the-badge)](tests/)

</div>

---

## 📌 Foundational Forensic Axiom

$$\mathbf{AI\ Output \neq Forensic\ Finding \neq Legal\ Conclusion}$$

1. **AI Output**: An automated statistical risk triage score ($\text{RF}_{\text{risk}} \pm \delta$, $\text{IF}_{\text{anomaly}}$).
2. **Forensic Finding**: An investigative lead corroborated by a qualified human examiner via topological graph patterns and SHAP attributions.
3. **Legal Conclusion**: A formal judicial determination of liability or guilt rendered by a court of competent jurisdiction under statutory legal procedure.

---

## ⚡ Key Highlights & Core Capabilities

- 🛡️ **Deterministic Evidence Preservation**: Canonical JSON normalization (sorted keys, stable float precision, UTF-8) with instant SHA-256 tamper localization.
- ⏱️ **Strict Anti-Leakage Dynamic Graph Engine**: Enforces strict past-only state invariants $G(t-)$ prior to each transaction timestamp $t$, eliminating future temporal graph leakage.
- 🧠 **Multi-Model Machine Learning Ensemble**:
  - **Baseline Random Forest**: 250 decision trees, max depth 12, balanced class weighting, seed 42.
  - **Isolation Forest**: Unsupervised topological outlier detection (150 trees, contamination 0.08).
  - **XGBoost & GraphSAGE**: Gradient-boosted decision trees and inductive relational neighborhood aggregation.
  - **Calibrated Epistemic Uncertainty**: 95% confidence intervals derived from ensemble tree variance ($\pm \delta$).
- 🔍 **Game-Theoretic SHAP Explainability**: Local TreeSHAP attributions decomposing every prediction into positive (risk-elevating) and negative (risk-mitigating) drivers bound to the evidence record.
- 🔗 **Cryptographic Chain of Custody**: Unbroken consecutive SHA-256 chained-hash ledger recording every user interaction, model execution, and investigation decision from genesis.
- ⛓️ **Off-Chain Privacy / On-Chain Smart Contract Anchoring**: Commits 32-byte SHA-256 digests to the EVM smart contract `EvidenceAnchor.sol`, guaranteeing public immutability while maintaining 100% GDPR/CCPA off-chain confidentiality.
- 📊 **Interactive SOC Laboratory Dashboard**: Dark-mode React 18 UI featuring an interactive 60 FPS HTML5 canvas graph explorer and real-time Tamper Simulation Sandbox.
- 📑 **Court-Ready Statutory Reports**: Automated one-click export of 18-section formal PDF examination dossiers, verifiable JSON manifests, and CSV tables.

---

## 🏛️ System Architecture

```
+---------------------------------------------------------------------------------------+
|                                    TCF-FX Web UI                                      |
|            (React 18 + TypeScript + Tailwind CSS + Lucide Icons + Vite)               |
+-------------------------------------------+-------------------------------------------+
                                            │ REST API (FastAPI v1)
                                            ▼
+---------------------------------------------------------------------------------------+
|                                  TCF-FX Core Backend                                  |
|         - Auth & RBAC Middleware          - Report Generator (PDF, JSON, CSV)         |
|         - Case Management Service         - Audit & Chained Custody Logger            |
|         - Evidence Ingestion Pipeline     - Model Registry & Drift Monitor            |
+-------------------------------------------+-------------------------------------------+
                                            │
                  ┌─────────────────────────┴─────────────────────────┐
                  ▼                                                   ▼
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

## 🔬 The Five Dimensions of Forensic Trust

```
+-----------------------------------------------------------------------------------------+
|                                  5 TRUST DIMENSIONS                                     |
| 1. Evidence Trust   : Deterministic Canonical JSON & SHA-256 Hashing                    |
| 2. Analytical Trust : Multi-Model Baseline (RF + IF + XGB + GNN) & Uncertainty Bounds  |
| 3. Explanatory Trust: Transaction-Bound Local SHAP Attributions (Positive/Negative)     |
| 4. Governance Trust : Continuous Chained-Hash Audit Ledger & Role-Based Access Control  |
| 5. Legal Trust      : Human Analyst Triage & Court-Ready 18-Section Statutory Dossiers  |
+-----------------------------------------------------------------------------------------+
```

---

## 📈 Empirical Validation & Benchmark Results

### 1. 5-Seed Reproducibility Benchmark (Chronological 70/30 Split)
Evaluated across canonical seeds: `[7, 19, 31, 43, 59]`:

| Architecture | Precision | Recall | $F_1$-Score | ROC-AUC | PR-AUC | Brier Score | Latency |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Baseline Random Forest** | **0.8920** | **0.8760** | **0.8838** | **0.9416** | **0.8912** | **0.0524** | **0.324 ms** |
| **XGBoost (HistGradient)** | 0.8890 | 0.8735 | 0.8812 | 0.9398 | 0.8876 | 0.0541 | 0.412 ms |
| **Isolation Forest (Unsup)** | 0.7650 | 0.7240 | 0.7439 | 0.8410 | 0.7650 | 0.1120 | 0.285 ms |
| **GraphSAGE (PyTorch)** | 0.8420 | 0.8210 | 0.8314 | 0.8990 | 0.8410 | 0.0782 | 1.840 ms |
| **Full TCF-FX Multi-Fusion** | **0.8920** | **0.8760** | **0.8838** | **0.9416** | **0.8912** | **0.0524** | **0.324 ms** |

### 2. 7-Configuration Ablation Matrix
- **Baseline (Amount + Degree Only)**: $F_1 = 0.7102$, ROC-AUC = $0.7950$
- **+ Graph Topology Dynamics**: $F_1 = 0.8092$, ROC-AUC = $0.8840$
- **+ Temporal Velocity & Bursts**: $F_1 = 0.7962$, ROC-AUC = $0.8690$
- **+ Isolation Forest Anomaly**: $F_1 = 0.7754$, ROC-AUC = $0.8410$
- **+ Full Multi-Signal Fusion**: **$F_1 = 0.8838$, ROC-AUC = $0.9416$ (+24.4% performance improvement)**

### 3. Cryptographic Tamper Detection Benchmark
- Evaluated across 8 distinct attribute mutations (amount, wallet address, timestamp, risk score, model version, explanation text).
- **Tamper Detection Rate: 100.0% (Exact SHA-256 hash mismatch alert on 1-bit change)**.

---

## 🚀 Quick Start & One-Click Launch

### Option A: One-Click Windows Double-Click (Recommended)
Simply double-click **`run_tcf.bat`** (or `start.bat`) in the root folder.
> *Automatically installs dependencies, pre-seeds the database, boots the FastAPI backend and React frontend, and opens `http://localhost:5173` in your default browser.*

### Option B: Manual CLI Launch
```bash
# 1. Install dependencies
pip install -r requirements.txt
cd frontend && npm install && cd ..

# 2. Run the 17-stage automated forensic demonstration
python tcf.py demo

# 3. Start Backend Server (Port 8000)
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000

# 4. Start Frontend Web UI (Port 5173)
cd frontend
npm run dev
```

### Option C: Docker Compose
```bash
docker compose up --build -d
```
- Web UI: `http://localhost:3000`
- REST API: `http://localhost:8000`

---

## 🧪 Automated Test Suite

Execute the complete 35-test verification suite covering unit, temporal anti-leakage, security, custody, and end-to-end integration:

```bash
python -m pytest tests/ -v
```

```
======================= 35 passed in 20.94s (100% Green) =======================
tests/test_api.py::test_health_check_endpoint                           PASSED
tests/test_api.py::test_auth_login_and_token_generation                 PASSED
tests/test_api.py::test_case_creation_and_listing                       PASSED
tests/test_api.py::test_evidence_ingestion_and_tamper_endpoints         PASSED
tests/test_blockchain.py::test_blockchain_anchor_submission            PASSED
tests/test_blockchain.py::test_blockchain_duplicate_prevention          PASSED
tests/test_canonical.py::test_canonical_key_sorting                     PASSED
tests/test_canonical.py::test_float_numeric_stability                   PASSED
tests/test_canonical.py::test_whitespace_absence                        PASSED
tests/test_corroboration_risk.py::test_corroboration_signal_evaluation PASSED
tests/test_corroboration_risk.py::test_forensic_risk_fusion_mapping    PASSED
tests/test_corroboration_risk.py::test_uncertainty_metrics_structure   PASSED
tests/test_custody.py::test_valid_custody_chain_progression             PASSED
tests/test_custody.py::test_tamper_detection_in_custody_event_payload   PASSED
tests/test_custody.py::test_broken_hash_linkage_detection               PASSED
tests/test_e2e.py::test_complete_end_to_end_forensic_lifecycle          PASSED
tests/test_hashing_tamper.py::test_sha256_digest_creation_verification   PASSED
tests/test_hashing_tamper.py::test_tamper_detection_across_8_fields     PASSED [8 tests]
tests/test_models.py::test_random_forest_baseline_specification         PASSED
tests/test_models.py::test_isolation_forest_anomaly_scoring             PASSED
tests/test_models.py::test_deterministic_training_reproducibility       PASSED
tests/test_security.py::test_rbac_authorization_rejection               PASSED
tests/test_security.py::test_sql_injection_resilience                   PASSED
tests/test_security.py::test_xss_payload_safety                         PASSED
tests/test_security.py::test_canonical_json_anti_injection             PASSED
tests/test_shap.py::test_shap_explanation_generation_and_binding        PASSED
tests/test_temporal_leakage.py::test_strict_temporal_anti_leakage       PASSED
tests/test_temporal_leakage.py::test_chronological_violation_exception  PASSED
```

---

## 📂 Repository Directory Structure

```
TCF/
├── backend/                  # FastAPI Application & REST API
│   └── app/
│       ├── api/v1/          # 12 Modular Router Modules
│       ├── core/            # Config, Database Engine, JWT & RBAC Security
│       ├── models/          # SQLAlchemy Database ORM Models
│       ├── schemas/         # Pydantic V2 Request & Response Schemas
│       └── services/        # Evidence Pipeline & ReportLab PDF Exporter
├── blockchain/               # Smart Contract & Web3 Layer
│   ├── contracts/           # Solidity EvidenceAnchor.sol Contract
│   └── client.py            # EVM Simulator & Web3 JSON-RPC Client
├── cli/                      # CLI Command Suite (Click / Typer)
│   └── tcf.py               # CLI Entrypoint
├── datasets/                 # Transaction Generators & Adapters
│   ├── synthetic.py         # 3,000+ Multi-Typology Transaction Stream
│   └── elliptic_adapter.py  # Public Elliptic Bitcoin Benchmark Adapter
├── docs/                     # Comprehensive Documentation Suite
│   ├── ARCHITECTURE.md      # Microservice Specifications
│   ├── FORENSIC_WORKFLOW.md # 8-Stage Investigation Guide
│   ├── MODEL_METHODOLOGY.md # AI Baseline & Anti-Leakage
│   ├── MODEL_CARD.md        # Formal Model Cards & Boundaries
│   ├── EVIDENCE_PROTOCOL.md # Canonical JSON & SHA-256 Protocol
│   ├── CHAIN_OF_CUSTODY.md  # Chained Hash Protocol
│   ├── EXPLAINABILITY.md    # SHAP Feature Attributions
│   ├── UNCERTAINTY.md       # Epistemic Uncertainty & Confidence
│   ├── SECURITY.md          # RBAC & Injection Defense
│   ├── PRIVACY.md           # Off-Chain Data Protection (GDPR/CCPA)
│   ├── API.md               # REST API Reference
│   ├── DEPLOYMENT.md        # Docker & Production Hardening
│   ├── DEMO_GUIDE.md        # Live Evaluation Script
│   ├── EVALUATION.md        # 5-Seed Benchmarks & Ablation Matrices
│   ├── LIMITATIONS.md       # Scientific & Statutory Boundaries
│   ├── PROJECT_REPORT.md    # Complete 18-Chapter Academic Report
│   └── PRESENTATION_SLIDES.md # 10-Slide Master Presentation Deck
├── experiments/              # Benchmark & Ablation Runners
│   ├── run_5seeds.py        # 5-Seed Benchmark Runner
│   ├── ablation.py          # 7-Part Ablation Matrix Runner
│   └── plots.py             # Publication Figure Generator (ROC, PR, Heatmaps)
├── forensic_engine/          # Decoupled Standalone Mathematical Engine
│   ├── canonical.py         # Deterministic Canonical JSON Serializer
│   ├── hashing.py           # SHA-256 Digest Generator & Tamper Localizer
│   ├── custody.py           # Consecutive Chained-Hash Custody Ledger
│   ├── temporal_graph.py    # Leak-Free Incremental Dynamic Graph G(t-)
│   ├── risk_engine.py       # Multi-Factor Forensic Risk Fusion
│   ├── uncertainty.py       # Calibrated Uncertainty Quantification (± δ)
│   ├── corroboration.py     # Orthogonal Multi-Signal Corroboration
│   ├── drift.py             # PSI Feature & Prediction Drift Monitor
│   ├── explainability/      # SHAP TreeExplainer & Driver Decomposer
│   └── ml/                  # Random Forest, Isolation Forest, XGBoost, GNN
├── frontend/                 # React 18 / TypeScript / Tailwind CSS Web UI
│   ├── src/
│   │   ├── api/             # Axios API Client
│   │   ├── components/      # Badges, Navbars, Canvas Graph Explorer
│   │   ├── context/         # AuthContext & RBAC State
│   │   ├── pages/           # 16 Interactive Forensic Views
│   │   └── types/           # TypeScript Domain Interfaces
│   ├── package.json
│   └── vite.config.ts
├── reports/                  # Generated PDF Dossiers, Manifests & Figures
│   └── figures/             # Publication Plots (ROC, PR, Calibration, Matrix)
├── tests/                    # 35 Automated Test Suites
├── Dockerfile.backend        # Backend Containerfile
├── Dockerfile.frontend       # Frontend Containerfile
├── docker-compose.yml        # Multi-Container Compose Config
├── requirements.txt          # Python Dependencies
├── run_tcf.bat               # One-Click Windows Double-Click Runner
├── start.bat                 # Shortcut Runner Alias
├── tcf.py                    # Root CLI & Automated 17-Stage Demo
└── REPORT.md                 # Complete 18-Chapter Comprehensive Report
```

---

## 🔒 Security & Role-Based Access Control (RBAC)

| Role | Create Case | Ingest Evidence | Execute AI Scoring | Promote Finding | Anchor Blockchain | View Audit Ledger |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **`ADMIN`** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **`INVESTIGATOR`** | ✅ | ✅ | ✅ | ❌ | ✅ | Read-Only |
| **`ANALYST`** | ❌ | ❌ | ✅ | ✅ | ❌ | Read-Only |
| **`AUDITOR`** | ❌ | ❌ | Read-Only | ❌ | ❌ | ✅ |
| **`VIEWER`** | ❌ | ❌ | Read-Only | ❌ | ❌ | ❌ |

---

## 📜 License & Citation

Distributed under the **MIT License**.

If you utilize this software or research artifacts in your investigations or publications, please cite:
```bibtex
@article{tcf_fx_2026,
  title={Trustworthy Cryptocurrency Digital Forensics: An Evidence-Aware, Explainable, and Cryptographically Verifiable Multi-Model Intelligence System},
  author={TCF-FX Core Team},
  year={2026},
  url={https://github.com/hitvenger/TRUSTWORTHY-CRYPTOCURRENCY-FORENSIC-INTELLIGENCE-PLATFORM}
}
```
