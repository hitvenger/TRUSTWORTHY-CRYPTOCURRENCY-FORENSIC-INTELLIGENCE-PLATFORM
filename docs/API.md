# REST API Reference Manual

## Base URL: `/api/v1`

### Case Endpoints
- `POST /cases`: Initialize a new forensic case and record genesis custody event.
- `GET /cases`: List all cases with evidence counts and lead summaries.
- `GET /cases/{case_id}`: Retrieve detailed case metadata.
- `PATCH /cases/{case_id}/status`: Update case status (`ACTIVE`, `UNDER_REVIEW`, `CLOSED`, `ARCHIVED`).

### Evidence & Integrity Endpoints
- `POST /cases/{case_id}/evidence`: Ingest, extract temporal features, score, and hash a new evidence record.
- `GET /cases/{case_id}/evidence`: List all evidence items in a case.
- `GET /evidence/{evidence_id}`: Fetch detailed evidence item by ID.
- `POST /evidence/{evidence_id}/verify`: Recompute and verify SHA-256 digest.
- `POST /evidence/{evidence_id}/tamper`: Inject malicious field value to simulate tampering.
- `POST /evidence/{evidence_id}/restore`: Restore original value and re-verify digest.
- `POST /evidence/{evidence_id}/anchor`: Submit SHA-256 digest to smart contract.

### Transaction & AI Endpoints
- `POST /transactions/analyze`: Real-time transaction scoring and SHAP feature attribution.
- `GET /transactions/{tx_id}/explanation`: Retrieve positive/negative decision drivers for a transaction.
- `GET /graph/explore`: Retrieve nodes (wallets) and directed edges (transactions) with risk filters.

### Reports & Audit Endpoints
- `POST /reports/generate`: Request formal examination report generation.
- `GET /reports/{case_id}/pdf`: Download printable 18-section PDF dossier.
- `GET /reports/{case_id}/manifest`: Download canonical JSON evidence manifest.
- `GET /reports/{case_id}/csv`: Download CSV analytical export.
- `GET /audit/custody-chain/{case_id}`: Audit complete sequential chain-of-custody hash links.
