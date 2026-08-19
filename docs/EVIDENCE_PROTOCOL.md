# Canonical Evidence Protocol & Deterministic Hashing

## 1. Deterministic Canonical Serialization Rules
To satisfy evidentiary integrity standards, two identical forensic records must generate identical byte sequences across all platforms:
1. **Sorted Keys**: Dictionary keys are sorted alphabetically at every level of nesting.
2. **Standard Separators**: Exact separators `(',', ':')` without trailing spaces or newline variances.
3. **Uniform Floating-Point Precision**: Numbers are normalized to 8 decimal places to avoid IEEE-754 representation noise.
4. **UTF-8 Encoding**: Character data is encoded strictly as UTF-8 bytes.

---

## 2. SHA-256 Digest Computation
```python
def create_digest(record: Dict[str, Any]) -> str:
    clean = {k: v for k, v in record.items() if k != "integrity_digest"}
    raw_bytes = canonical_json_bytes(clean)
    return hashlib.sha256(raw_bytes).hexdigest()
```
Modifying even a single character in any field (amount, timestamp, wallet, risk score) immediately results in a complete cryptographic hash divergence.
