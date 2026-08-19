# Security Architecture & Access Control (RBAC)

## 1. Role-Based Access Control (RBAC)
TCF-FX enforces strict separation of duties across 5 roles:
- **`ADMIN`**: User management, system configuration, model recalibration approvals.
- **`INVESTIGATOR`**: Case creation, evidence acquisition, pipeline execution, on-chain anchoring.
- **`ANALYST`**: Triage review, finding promotions, corroboration assessment, report generation.
- **`AUDITOR`**: Read-only access to cryptographic chains of custody, tamper audits, and logs.
- **`VIEWER`**: Read-only access to published non-sensitive case summaries.

---

## 2. Security Hardening
- **Injection Protection**: Parameterized SQLAlchemy ORM queries preventing SQL injection; JSON schema sanitization preventing XSS attacks.
- **Cryptographic Hashing**: SHA-256 digests over deterministic canonical representations.
- **Security Headers**: `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `X-XSS-Protection: 1; mode=block`.
