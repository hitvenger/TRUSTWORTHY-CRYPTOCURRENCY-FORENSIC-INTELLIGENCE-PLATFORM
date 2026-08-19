"""
Canonical JSON Serializer for TCF-FX Forensic Platform.

Guarantees deterministic, reproducible byte representations across platforms
for cryptographic hashing and digital evidence integrity verification.
"""

import json
from typing import Any, Union, Dict, List
import math


def normalize_value(val: Any) -> Any:
    """Recursively normalizes objects for deterministic serialization."""
    if val is None:
        return None
    elif isinstance(val, bool):
        return val
    elif isinstance(val, int):
        return val
    elif isinstance(val, float):
        if math.isnan(val) or math.isinf(val):
            return None
        # Format float deterministically: standard 8 decimal places if needed or round
        # Avoid float precision artifacts like 0.30000000000000004
        rounded = round(val, 8)
        if rounded.is_integer():
            return int(rounded)
        return rounded
    elif isinstance(val, str):
        return val
    elif isinstance(val, (list, tuple, set)):
        return [normalize_value(item) for item in val]
    elif isinstance(val, dict):
        # Sort keys deterministically
        return {str(k): normalize_value(v) for k, v in sorted(val.items(), key=lambda x: str(x[0]))}
    elif hasattr(val, "to_dict") and callable(val.to_dict):
        return normalize_value(val.to_dict())
    elif hasattr(val, "__dict__"):
        return normalize_value(val.__dict__)
    else:
        return str(val)


def canonical_json_dumps(obj: Any) -> str:
    """
    Serializes a Python object into a canonical, deterministic JSON string.
    Rules:
    - Recursively sorted dictionary keys
    - Deterministic separators with zero unnecessary whitespace (',', ':')
    - Uniform numeric normalization
    - UTF-8 compatible
    """
    normalized = normalize_value(obj)
    return json.dumps(
        normalized,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False
    )


def canonical_json_bytes(obj: Any) -> bytes:
    """
    Returns canonical JSON representation as UTF-8 encoded bytes.
    Identical evidence records will ALWAYS produce identical byte arrays.
    """
    return canonical_json_dumps(obj).encode("utf-8")
