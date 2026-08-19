"""
Cryptographic Evidence Hashing & Tamper Detection for TCF-FX.

Implements SHA-256 hashing over canonical JSON bytes to verify forensic
integrity and pinpoint any deliberate or accidental field modifications.
"""

import hashlib
from typing import Any, Dict, Tuple, Optional
from forensic_engine.canonical import canonical_json_bytes, canonical_json_dumps


def create_digest(record: Dict[str, Any], exclude_digest_field: bool = True) -> str:
    """
    Computes a deterministic SHA-256 digest of an evidence record.
    Excludes the 'integrity_digest' field itself during computation.
    """
    clean_record = {k: v for k, v in record.items() if not (exclude_digest_field and k == "integrity_digest")}
    raw_bytes = canonical_json_bytes(clean_record)
    return hashlib.sha256(raw_bytes).hexdigest()


def verify_digest(record: Dict[str, Any], expected_digest: Optional[str] = None) -> Tuple[bool, str, Dict[str, Any]]:
    """
    Verifies the integrity of an evidence record.
    
    Returns:
        (is_valid, computed_digest, verification_metadata)
    """
    target_digest = expected_digest or record.get("integrity_digest")
    if not target_digest:
        return False, "", {"status": "NO_DIGEST_PROVIDED", "error": "No expected digest found in record or parameter"}
    
    computed = create_digest(record, exclude_digest_field=True)
    is_valid = (computed.lower() == target_digest.lower())
    
    metadata = {
        "status": "VERIFIED" if is_valid else "TAMPER_DETECTED",
        "expected_digest": target_digest,
        "computed_digest": computed,
        "match": is_valid,
    }
    return is_valid, computed, metadata


def detect_tampering(original_record: Dict[str, Any], modified_record: Dict[str, Any]) -> Dict[str, Any]:
    """
    Detailed forensic comparison between original and candidate evidence records.
    Identifies exact mutated keys, value diffs, and cryptographic hash divergence.
    """
    orig_digest = create_digest(original_record)
    mod_digest = create_digest(modified_record)
    
    all_keys = set(original_record.keys()).union(set(modified_record.keys()))
    altered_fields = []
    
    for key in sorted(all_keys):
        if key == "integrity_digest":
            continue
        val_orig = original_record.get(key)
        val_mod = modified_record.get(key)
        if val_orig != val_mod:
            altered_fields.append({
                "field": key,
                "original_value": val_orig,
                "modified_value": val_mod,
                "status": "MUTATED" if (key in original_record and key in modified_record) else ("DELETED" if key in original_record else "ADDED")
            })
            
    is_tampered = (orig_digest != mod_digest) or len(altered_fields) > 0
    
    return {
        "is_tampered": is_tampered,
        "status": "TAMPER_DETECTED" if is_tampered else "INTEGRITY_VERIFIED",
        "original_digest": orig_digest,
        "candidate_digest": mod_digest,
        "altered_field_count": len(altered_fields),
        "altered_fields": altered_fields,
    }
