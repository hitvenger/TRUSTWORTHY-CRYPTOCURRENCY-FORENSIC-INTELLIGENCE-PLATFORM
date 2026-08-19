"""
Synthetic Forensic Dataset Generator for TCF-FX.

Generates 3,000+ realistic, chronologically ordered cryptocurrency transactions
incorporating complex forensic topologies:
- Exchange Hubs & Liquidity Pools
- Mixing / Peeling Chains
- Fan-out Rapid Dispersal
- Fan-in Consolidation
- Dormant Wallet Activations
- High-velocity Wash Trading Cycles
- Controlled Label Noise & Deterministic Seeds
"""

import random
import uuid
import datetime
import numpy as np
from typing import List, Dict, Any, Optional


def generate_wallet_address(prefix: str, index: int) -> str:
    """Generates deterministic realistic-looking crypto wallet addresses."""
    # Deterministic hex suffix based on index
    suffix = hex(abs(hash(f"{prefix}_{index}")))[2:].zfill(38)[:38]
    if prefix.startswith("0x"):
        return f"0x{suffix}"
    return f"bc1q{suffix[:38]}"


def generate_synthetic_dataset(
    num_transactions: int = 3500,
    seed: int = 42,
    illicit_ratio: float = 0.12,
    start_timestamp: Optional[float] = None
) -> List[Dict[str, Any]]:
    """
    Generates a synthetic forensic transaction stream.
    Returns list of dicts: [tx_id, src, dst, amount, timestamp, label, pattern_type]
    """
    random.seed(seed)
    np.random.seed(seed)

    if start_timestamp is None:
        start_timestamp = 1704067200.0  # 2024-01-01 00:00:00 UTC

    # Create pool of entities:
    # 5 exchanges, 20 high-activity merchants, 300 standard users, 15 darknet/mixing clusters
    exchanges = [generate_wallet_address("0x_exch", i) for i in range(6)]
    merchants = [generate_wallet_address("0x_merch", i) for i in range(25)]
    standard_users = [generate_wallet_address("0x_user", i) for i in range(400)]
    illicit_rings = [
        [generate_wallet_address(f"0x_illicit_ring_{r}", i) for i in range(8)]
        for r in range(12)
    ]

    transactions = []
    current_time = start_timestamp
    tx_counter = 0

    # Strategy: generate realistic mixture of benign background traffic + forensic illicit patterns
    while len(transactions) < num_transactions:
        # Step forward in time (0.5 to 120 seconds between events)
        time_delta = float(np.random.exponential(scale=35.0))
        current_time += max(1.0, time_delta)

        # Decide scenario type
        p = random.random()

        if p < (1.0 - illicit_ratio):
            # BENIGN TRANSACTION
            sub_p = random.random()
            if sub_p < 0.40:
                # User -> Exchange deposit
                src = random.choice(standard_users)
                dst = random.choice(exchanges)
                amt = round(float(np.random.lognormal(mean=2.0, sigma=1.2)), 4)
                pattern = "USER_EXCHANGE_DEPOSIT"
            elif sub_p < 0.70:
                # Exchange -> User withdrawal
                src = random.choice(exchanges)
                dst = random.choice(standard_users)
                amt = round(float(np.random.lognormal(mean=2.5, sigma=1.0)), 4)
                pattern = "EXCHANGE_WITHDRAWAL"
            elif sub_p < 0.90:
                # User -> Merchant payment
                src = random.choice(standard_users)
                dst = random.choice(merchants)
                amt = round(float(np.random.uniform(5.0, 350.0)), 2)
                pattern = "MERCHANT_PAYMENT"
            else:
                # Peer-to-Peer
                src = random.choice(standard_users)
                dst = random.choice(standard_users)
                while dst == src:
                    dst = random.choice(standard_users)
                amt = round(float(np.random.uniform(10.0, 1500.0)), 2)
                pattern = "P2P_TRANSFER"

            label = 0
            # 1.5% label noise / benign false lead
            if random.random() < 0.015:
                label = 1

            tx_counter += 1
            transactions.append({
                "transaction_id": f"tx_ben_{tx_counter:06d}",
                "source_wallet": src,
                "destination_wallet": dst,
                "amount": max(0.01, amt),
                "timestamp": current_time,
                "label": label,
                "pattern_type": pattern,
                "description": f"Standard {pattern.lower().replace('_', ' ')} transfer"
            })

        else:
            # ILLICIT / SUSPICIOUS FORENSIC PATTERN
            ring = random.choice(illicit_rings)
            pattern_choice = random.choice(["PEELING_CHAIN", "FAN_OUT_MIX", "FAN_IN_CONSOLIDATION", "WASH_CYCLE", "RAPID_DRAIN"])

            if pattern_choice == "PEELING_CHAIN":
                # Peeling chain: large amount forwarded through hops, peeling off small change
                initial_amt = float(np.random.uniform(40.0, 200.0))
                hop_src = ring[0]
                for hop_idx in range(1, min(5, len(ring))):
                    hop_dst = ring[hop_idx]
                    peel_amt = round(initial_amt * 0.1, 4)
                    forward_amt = round(initial_amt * 0.9, 4)
                    
                    tx_counter += 1
                    current_time += random.uniform(5.0, 45.0)  # Rapid hops
                    transactions.append({
                        "transaction_id": f"tx_ill_{tx_counter:06d}",
                        "source_wallet": hop_src,
                        "destination_wallet": hop_dst,
                        "amount": forward_amt,
                        "timestamp": current_time,
                        "label": 1,
                        "pattern_type": "PEELING_CHAIN",
                        "description": f"Peeling chain hop {hop_idx} forwarding {forward_amt} BTC"
                    })
                    hop_src = hop_dst
                    initial_amt = forward_amt
                    if len(transactions) >= num_transactions:
                        break

            elif pattern_choice == "FAN_OUT_MIX":
                # 1 source rapidly disbursing to 5 destinations
                f_src = ring[0]
                total_to_split = float(np.random.uniform(50.0, 300.0))
                split_targets = ring[1:6]
                split_amt = round(total_to_split / len(split_targets), 4)
                for f_dst in split_targets:
                    tx_counter += 1
                    current_time += random.uniform(2.0, 15.0)
                    transactions.append({
                        "transaction_id": f"tx_ill_{tx_counter:06d}",
                        "source_wallet": f_src,
                        "destination_wallet": f_dst,
                        "amount": split_amt,
                        "timestamp": current_time,
                        "label": 1,
                        "pattern_type": "FAN_OUT_DISPERSAL",
                        "description": f"High-velocity fan-out dispersal to {f_dst[:10]}..."
                    })
                    if len(transactions) >= num_transactions:
                        break

            elif pattern_choice == "FAN_IN_CONSOLIDATION":
                # Multiple intermediate wallets sending into 1 exit node
                c_dst = ring[-1]
                for c_src in ring[1:5]:
                    c_amt = round(float(np.random.uniform(10.0, 50.0)), 4)
                    tx_counter += 1
                    current_time += random.uniform(5.0, 30.0)
                    transactions.append({
                        "transaction_id": f"tx_ill_{tx_counter:06d}",
                        "source_wallet": c_src,
                        "destination_wallet": c_dst,
                        "amount": c_amt,
                        "timestamp": current_time,
                        "label": 1,
                        "pattern_type": "FAN_IN_CONSOLIDATION",
                        "description": f"Layering consolidation into exit node {c_dst[:10]}..."
                    })
                    if len(transactions) >= num_transactions:
                        break

            elif pattern_choice == "WASH_CYCLE":
                # Cyclical wash transfers: A -> B -> C -> A
                w_amt = round(float(np.random.uniform(30.0, 100.0)), 4)
                cycle_nodes = ring[:3]
                for c_idx in range(len(cycle_nodes)):
                    c_s = cycle_nodes[c_idx]
                    c_d = cycle_nodes[(c_idx + 1) % len(cycle_nodes)]
                    tx_counter += 1
                    current_time += random.uniform(10.0, 60.0)
                    transactions.append({
                        "transaction_id": f"tx_ill_{tx_counter:06d}",
                        "source_wallet": c_s,
                        "destination_wallet": c_d,
                        "amount": w_amt,
                        "timestamp": current_time,
                        "label": 1,
                        "pattern_type": "WASH_CYCLE",
                        "description": f"Wash trading cycle transfer {c_s[:8]} -> {c_d[:8]}"
                    })
                    if len(transactions) >= num_transactions:
                        break

            elif pattern_choice == "RAPID_DRAIN":
                # Sudden large drain from a previously dormant node
                drain_src = ring[2]
                drain_dst = random.choice(exchanges)
                d_amt = round(float(np.random.uniform(75.0, 500.0)), 4)
                tx_counter += 1
                current_time += random.uniform(20.0, 120.0)
                transactions.append({
                    "transaction_id": f"tx_ill_{tx_counter:06d}",
                    "source_wallet": drain_src,
                    "destination_wallet": drain_dst,
                    "amount": d_amt,
                    "timestamp": current_time,
                    "label": 1,
                    "pattern_type": "RAPID_DRAIN",
                    "description": f"Rapid liquidation of {d_amt} to exchange {drain_dst[:10]}..."
                })

    # Sort strictly chronologically to eliminate any generation artifacts
    transactions = sorted(transactions[:num_transactions], key=lambda x: x["timestamp"])
    return transactions
