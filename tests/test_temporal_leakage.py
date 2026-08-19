"""
Unit Tests for Strict Temporal Anti-Leakage Invariants in Graph Feature Extraction.
"""

import pytest
from forensic_engine.temporal_graph import IncrementalTemporalGraph


def test_strict_temporal_anti_leakage():
    """
    Asserts that at timestamp t_i, the source and destination wallets' features
    reflect ONLY historical transactions occurring before t_i, and do not contain
    any future degree, volume, or topological connections.
    """
    engine = IncrementalTemporalGraph()

    src = "0x_alice"
    dst = "0x_bob"

    # Transaction 1: Alice -> Bob (10 BTC at t=100)
    feats_1 = engine.extract_features_before_update("tx_1", src, dst, 10.0, 100.0)
    # Alice and Bob have zero prior transactions in G(100-)
    assert feats_1["src_in_degree"] == 0.0
    assert feats_1["src_out_degree"] == 0.0
    assert feats_1["src_total_degree"] == 0.0
    assert feats_1["dst_in_degree"] == 0.0

    # Update graph with tx_1
    engine.update_graph("tx_1", src, dst, 10.0, 100.0)

    # Transaction 2: Alice -> Bob (5 BTC at t=200)
    feats_2 = engine.extract_features_before_update("tx_2", src, dst, 5.0, 200.0)
    # Now Alice should have exactly 1 past outgoing tx, Bob has 1 past incoming tx
    assert feats_2["src_out_degree"] == 1.0
    assert feats_2["src_in_degree"] == 0.0
    assert feats_2["dst_in_degree"] == 1.0
    assert feats_2["src_out_mean"] == 10.0
    assert feats_2["src_time_since_last_tx"] == 100.0  # 200 - 100

    # Update graph with tx_2
    engine.update_graph("tx_2", src, dst, 5.0, 200.0)

    # Transaction 3: Alice -> Charlie (20 BTC at t=300)
    charlie = "0x_charlie"
    feats_3 = engine.extract_features_before_update("tx_3", src, charlie, 20.0, 300.0)
    assert feats_3["src_out_degree"] == 2.0
    assert feats_3["dst_in_degree"] == 0.0  # Charlie is new in G(300-)


def test_chronological_violation_exception():
    """
    Verifies that the temporal engine actively rejects out-of-order / backdated
    transactions when chronological assertions are enabled.
    """
    engine = IncrementalTemporalGraph()
    engine.update_graph("tx_1", "0x_a", "0x_b", 10.0, timestamp=500.0)

    # Attempt to extract features for a past timestamp t=400 after t=500 has been processed
    with pytest.raises(ValueError) as exc_info:
        engine.extract_features_before_update(
            "tx_late", "0x_a", "0x_b", 5.0, timestamp=400.0, assert_chronological=True
        )

    assert "Temporal Leakage Violation" in str(exc_info.value)
