# Privacy & Data Protection Architecture

## 1. Off-Chain Confidentiality Principle
TCF-FX strictly adheres to privacy by design:
- **Never Record Raw Evidence On-Chain**: Personal identifiable information (PII), full transaction memos, and wallet IP linkages are stored strictly off-chain in encrypted local databases.
- **On-Chain Anchor Minimalization**: Only 32-byte SHA-256 evidence digests and timestamps are anchored onto public or consortium smart contracts.

---

## 2. Retention & Selective Disclosure
- Role-based redaction when exporting forensic dossiers.
- Cryptographic evidence verification does not require revealing the underlying payload if an investigator only shares the canonical SHA-256 digest with an external authority.
