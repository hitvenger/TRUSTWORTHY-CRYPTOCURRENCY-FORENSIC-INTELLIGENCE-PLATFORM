# Evaluator & Classroom Live Demonstration Script

## 1. Zero-Configuration Live Demonstration (`tcf demo`)
To execute the complete 17-stage investigation sequence live in the terminal:
```bash
python tcf.py demo
```

### Demonstration Steps Executed:
1. Initialize forensic database and tables.
2. Create case: `Operation ShadowChain - Illicit Layering & Mixer Investigation`.
3. Ingest 3,000+ chronologically ordered synthetic cryptocurrency transactions.
4. Construct incremental temporal graph with strict anti-leakage guards.
5. Execute baseline Random Forest (250 trees, max depth 12, balanced) and Isolation Forest.
6. Calculate multi-signal risk fusion and uncertainty margins.
7. Compute SHAP decision attributions for positive/negative drivers.
8. Deterministically serialize canonical JSON and compute SHA-256 digest.
9. Verify original evidence integrity (`INTEGRITY VERIFIED`).
10. Deliberately mutate transaction amount to simulate malicious tampering.
11. Re-verify to demonstrate tamper detection (`TAMPER DETECTED!`).
12. Restore valid evidence and verify recovery (`INTEGRITY RE-VERIFIED`).
13. Anchor evidence digest to Solidity smart contract.
14. Independently verify on-chain blockchain anchor.
15. Audit digital chain of custody hash links.
16. Execute human analyst review and promote investigative lead to `FORENSIC_FINDING`.
17. Generate court-ready PDF dossier, canonical JSON manifest, and CSV export.

---

## 2. Interactive Web UI Demonstration Flow
1. Open browser at `http://localhost:5173`.
2. Inspect **Dashboard**: Review risk distribution, active leads, and AI engine status.
3. Open **Investigation Graph**: Zoom, pan, and click on nodes to inspect wallet flow metrics.
4. Open **Evidence Dossier**: View canonical JSON, click "Inject Tamper" to witness the real-time tamper alert, then click "Restore" to confirm cryptographic recovery.
5. Open **Reports**: Download formal PDF Examination Report.
