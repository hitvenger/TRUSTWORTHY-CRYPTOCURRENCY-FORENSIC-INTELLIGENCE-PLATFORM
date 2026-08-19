# TCF-FX — Complete Forensic Intelligence System & Technical Whitepaper

> **Title**: Trustworthy Cryptocurrency Digital Forensics: System Architecture, Evidentiary Methodology, and Multi-Model Intelligence  
> **Platform Name**: TCF-FX (Trustworthy Cryptocurrency Forensic Intelligence Platform)  
> **Version**: 1.0.0 (Research-Grade & Production Deployment Specification)

---

## 1. What This System and Model Does

### Executive Summary
**TCF-FX** is an end-to-end digital forensics intelligence application engineered for cryptocurrency fraud investigations, illicit transaction tracing, and evidence integrity preservation. Derived directly from the research paper *"Trustworthy Cryptocurrency Digital Forensics: A Critical Synthesis and Reproducible Proof-of-Concept"*, the system addresses the critical gap between raw machine learning classifiers and admissible forensic evidence.

Unlike generic machine learning demonstrators, TCF-FX provides a complete evidentiary pipeline that:
1. **Acquires & Preserves Evidence**: Ingests raw UTXO/account cryptocurrency transactions and computes deterministic canonical SHA-256 integrity digests.
2. **Builds Anti-Leakage Temporal Graphs**: Constructs directed transaction graphs where graph topology strictly reflects state $G(t-)$ prior to each transaction timestamp $t$, eliminating future information leakage.
3. **Executes Multi-Model AI Risk Scoring**: Combines a 250-tree balanced Random Forest classifier, unsupervised Isolation Forest anomaly detection, and topological feature extraction.
4. **Provides Local SHAP Decision Attributions**: Explains exactly which positive features elevated transaction risk and which negative features mitigated risk, binding the rationale to the evidence record.
5. **Enforces Cryptographic Chain of Custody**: Links every user action, model evaluation, and investigation update in an unbroken SHA-256 chained-hash ledger.
6. **Anchors Off-Chain Evidence to Smart Contracts**: Commits SHA-256 digests to the Ethereum Virtual Machine (EVM) smart contract `EvidenceAnchor.sol`, guaranteeing public immutability while protecting off-chain investigation privacy.
7. **Produces Court-Ready Forensic Dossiers**: Automatically compiles 18-section formal PDF examination reports, canonical JSON manifests, and CSV tables.

---

## 2. Why and How It Is Related to Digital Forensics

### The Core Problem in Cryptocurrency Investigations
Traditional machine learning classification faces severe challenges in judicial and forensic contexts:
1. **The "Black Box" Problem**: Complex neural networks or ensembles output probabilities (e.g. `0.94`) without explaining *why* an address was flagged, violating evidentiary standards such as the US *Daubert* standard or UK *PACE* rules.
2. **Evidence Tampering Vulnerability**: Storing analytical scores or transaction tables in mutable databases allows internal or external manipulation without detection.
3. **Temporal Information Leakage**: Standard ML models compute graph metrics (e.g. PageRank, clustering) over an entire historical dataset, allowing future data to "leak" into past predictions—invalidating empirical validity.
4. **Conflation of Algorithmic Output with Legal Proof**: Automated systems often erroneously treat probabilistic scores as legal proof of guilt.

### How TCF-FX Enforces Digital Forensics Integrity

#### A. The Foundational Forensic Axiom
$$\mathbf{AI\ Output \neq Forensic\ Finding \neq Legal\ Conclusion}$$
- **AI Output**: A statistical triage score (e.g. Random Forest risk $0.801 \pm 0.25$, Isolation Forest anomaly $0.512$).
- **Forensic Finding**: A validated investigative lead corroborated by a human analyst after reviewing topological graph patterns and SHAP decision drivers.
- **Legal Conclusion**: A judicial determination of liability or guilt made by a court of competent jurisdiction following statutory legal procedure.

#### B. The 5 Trust Dimensions
Every component of TCF-FX maps directly to one of the 5 Trust Dimensions established in the paper:
```
           +-------------------------------------------------------------+
           |                    5 TRUST DIMENSIONS                       |
           +-------------------------------------------------------------+
           | 1. Evidence Trust   : Canonical SHA-256 serialization       |
           | 2. Analytical Trust : Multi-model risk & uncertainty fusion |
           | 3. Explanatory Trust: Transaction-bound SHAP attributions   |
           | 4. Governance Trust : Continuous chained audit logging      |
           | 5. Legal Trust      : Human review & statutory reporting    |
           +-------------------------------------------------------------+
```

#### C. The 8-Stage Digital Forensics Lifecycle
```
[1. Acquisition] ──► Structured transaction ingestion & provenance recording
       │
[2. Preservation] ──► Deterministic Canonical JSON & SHA-256 Hashing
       │
[3. Temporal Graph] ──► Dynamic feature extraction on G(t-) without future leakage
       │
[4. AI Scoring] ──► Multi-model inference (Random Forest + Isolation Forest)
       │
[5. XAI Attribution] ──► SHAP decision drivers (+ and - impact decomposition)
       │
[6. Human Review] ──► Analyst promotion to FORENSIC_FINDING with documented rationale
       │
[7. Anchoring] ──► Commit SHA-256 digest to Solidity smart contract
       │
[8. Reporting] ──► Generate formal 18-section PDF dossier & JSON manifest
```

---

## 3. What Is Required (System Requirements & Dependencies)

### Software & Environment Requirements:
- **Python**: Python 3.11+
- **Node.js**: Node.js 18+ & npm 9+
- **Database**: SQLite (default zero-config) or PostgreSQL (production)
- **Solidity / EVM**: Embedded simulated EVM client or Web3 JSON-RPC provider (e.g. Infura / Alchemy / Ganache)

### Core Python Dependencies:
- `fastapi`, `uvicorn`, `pydantic-settings`: High-performance asynchronous REST API backend.
- `scikit-learn`, `numpy`, `pandas`: Machine learning baseline and evaluation metrics.
- `shap`: Local TreeExplainer game-theoretic feature attributions.
- `xgboost`, `torch`: Comparative gradient boosting and inductive GraphSAGE neural network models.
- `reportlab`: Formal 18-section PDF forensic examination report generation.
- `web3`, `eth-account`: Blockchain evidence smart contract interaction.
- `networkx`: Directed topological cryptocurrency graph modeling.
- `pytest`, `pytest-asyncio`, `httpx`: Complete automated verification test suite.

### Frontend Technology Stack:
- `React 18`, `TypeScript`, `Tailwind CSS`: SOC dark-mode dashboard interface.
- `Vite`: Lightning-fast ES module bundler.
- `Lucide React`: Security and forensic vector iconography.
- `HTML5 2D Canvas`: Interactive directed graph visualization.

---

## 4. Deep Architectural Breakdown

### 4.1 Deterministic Canonical Serialization & Tamper Detection
To ensure that two identical evidence objects always produce the exact same SHA-256 digest regardless of runtime environment, `forensic_engine/canonical.py` enforces:
1. **Alphabetically Sorted Keys**: Recursively sorted keys at all nested levels.
2. **Stable Float Precision**: Floats normalized to 8 decimal places (`"%.8f"`), eliminating floating-point architecture variances.
3. **No Superfluous Whitespace**: Uniform JSON separators `(',', ':')`.
4. **UTF-8 Byte Encoding**: Strict normalization preventing character set differences.

**Tamper Detection Mechanism**:
If an attacker or corrupted process alters even 1 bit in any field:
$$\text{SHA-256}(\text{Canonical}(\text{Record}_{\text{tampered}})) \neq \text{Stored\_Digest}$$
The system immediately raises a `TAMPER DETECTED!` security alert and localizes the modified field.

### 4.2 Anti-Leakage Incremental Temporal Graph
In cryptocurrency forensics, calculating metrics like *wallet velocity*, *clustering coefficient*, or *k-hop exposure* across an entire dataset introduces **future leakage**.

TCF-FX guarantees zero leakage via `forensic_engine/temporal_graph.py`:
- For each transaction $tx_i = (\text{src}, \text{dst}, \text{amt}, t_i)$:
  1. Verify chronological monotonicity: $t_i \ge t_{\text{prev}}$.
  2. Extract features strictly from historical graph state $G(t_i^-)$.
  3. Execute model inference and SHAP calculation.
  4. Only then update the graph state to $G(t_i)$ by inserting directed edge $(\text{src} \to \text{dst})$.

### 4.3 Multi-Model Machine Learning Suite
1. **Paper Baseline Random Forest** (`RandomForestClassifier`):
   - $250$ Trees, $\text{Max Depth } 12$, `class_weight='balanced'`, `random_state=42`.
   - Produces calibrated supervised risk probability $p \in [0.0, 1.0]$.
2. **Isolation Forest** (`IsolationForest`):
   - $150$ Trees, `contamination=0.08`.
   - Provides orthogonal unsupervised topological outlier detection.
3. **Epistemic Uncertainty Quantification**:
   - Computes standard error across the 250 individual tree predictions $\sigma_{\text{trees}}$.
   - Calculates 95% confidence margins: $\text{Uncertainty} = \pm 1.96 \cdot \sigma_{\text{trees}}$.
4. **Multi-Signal Corroboration**:
   - Synthesizes supervised probability, unsupervised anomaly ranking, velocity bursts, and k-hop flagged exposures into qualitative corroboration levels: `NONE`, `WEAK`, `MODERATE`, `STRONG`.

### 4.4 Transaction-Bound SHAP Explainability
`forensic_engine/explainability/shap_engine.py` uses Shapley additive explanations to break down the model's decision:
$$f(x) = \phi_0 + \sum_{j=1}^{M} \phi_j$$
- $\phi_0$: Dataset base rate risk.
- $\phi_j > 0$: Features pushing the risk score upward (e.g. *high hourly velocity*, *rapid downstream drain*).
- $\phi_j < 0$: Features reducing risk (e.g. *long wallet tenure*, *high counterparty diversity*).

### 4.5 Digital Chain of Custody
Every action (case creation, evidence ingestion, model execution, analyst review, report export) creates an immutable chained hash event:
$$\text{Hash}_k = \text{SHA-256}\Big(\text{Canonical}\big(\text{Hash}_{k-1}, \text{Actor}, \text{Role}, \text{Action}, \text{Timestamp}, \text{Payload}\big)\Big)$$
- Genesis event links to `0000000000000000000000000000000000000000000000000000000000000000`.
- Broken hash links or mutated logs are immediately detected during integrity audits.

### 4.6 Blockchain Smart Contract Anchoring
`blockchain/contracts/EvidenceAnchor.sol` provides on-chain immutability:
- **Off-Chain Privacy**: Raw transactions, wallet linkages, and investigator notes remain strictly off-chain in local databases.
- **On-Chain Digest**: Only `bytes32 evidenceId` and `bytes32 sha256Digest` are committed on-chain.
- **Duplicate Protection**: Smart contract rejects duplicate submissions of identical evidence IDs.
- **Court Admissibility**: Provides mathematical proof that a specific piece of evidence existed in an exact state at or before block number $N$.

---

## 5. Summary Table: Trust Dimensions Mapping

| Trust Dimension | Technical Implementation | Forensic Role |
| :--- | :--- | :--- |
| **Evidence Trust** | Canonical JSON & SHA-256 Hashing | Proves evidence has not been altered since acquisition. |
| **Analytical Trust** | 250-Tree Random Forest + Isolation Forest + Uncertainty ($\pm \delta$) | Delivers rigorous multi-signal risk scoring without overconfidence. |
| **Explanatory Trust** | SHAP Local TreeExplainer Decomposition | Discloses exact decision drivers for each individual transaction. |
| **Governance Trust** | Continuous Chained Hash Ledger & RBAC | Records unbroken audit trail of every investigator action. |
| **Legal Trust** | Human Analyst Triage & 18-Section PDF Dossiers | Translates technical leads into admissible statutory reports. |
