"""
Unit Tests for Deterministic Canonical JSON Serialization.
"""

import pytest
import json
from forensic_engine.canonical import canonical_json_dumps, canonical_json_bytes, normalize_value


def test_canonical_key_sorting():
    obj1 = {"z_field": 100, "a_field": "test", "m_nested": {"k2": 2, "k1": 1}}
    obj2 = {"a_field": "test", "m_nested": {"k1": 1, "k2": 2}, "z_field": 100}

    dump1 = canonical_json_dumps(obj1)
    dump2 = canonical_json_dumps(obj2)

    assert dump1 == dump2
    assert canonical_json_bytes(obj1) == canonical_json_bytes(obj2)
    # Assert keys appear alphabetically
    assert dump1.startswith('{"a_field":"test","m_nested":{"k1":1,"k2":2},"z_field":100}')


def test_float_numeric_stability():
    obj_float1 = {"amount": 45.123456789}
    obj_float2 = {"amount": 45.12345679}  # Rounded to 8 decimals

    bytes1 = canonical_json_bytes(obj_float1)
    bytes2 = canonical_json_bytes(obj_float2)

    assert bytes1 == bytes2


def test_whitespace_absence():
    obj = {"key": "value", "list": [1, 2, 3]}
    canonical_str = canonical_json_dumps(obj)
    # Must use strictly (',', ':') with zero extraneous spaces
    assert ": " not in canonical_str
    assert ", " not in canonical_str
    assert canonical_str == '{"key":"value","list":[1,2,3]}'
