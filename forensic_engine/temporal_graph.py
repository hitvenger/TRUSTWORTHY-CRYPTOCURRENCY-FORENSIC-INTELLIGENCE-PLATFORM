"""
Incremental Temporal Graph Engine for TCF-FX.

Guarantees strict temporal anti-leakage:
For any transaction at timestamp t, features are extracted ONLY from the historical
graph state G(t-) containing events prior to t.
Only after feature extraction is G(t) updated with the current transaction.
"""

import math
import numpy as np
import networkx as nx
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass, field
from collections import defaultdict


@dataclass
class WalletHistoricalState:
    address: str
    first_seen_ts: float = 0.0
    last_seen_ts: float = 0.0
    tx_count: int = 0
    in_tx_count: int = 0
    out_tx_count: int = 0
    in_amounts: List[float] = field(default_factory=list)
    out_amounts: List[float] = field(default_factory=list)
    counterparties: set = field(default_factory=set)
    in_counterparties: set = field(default_factory=set)
    out_counterparties: set = field(default_factory=set)
    recent_tx_timestamps: List[float] = field(default_factory=list)
    recent_tx_amounts: List[float] = field(default_factory=list)
    known_suspicious_exposure_count: int = 0


class IncrementalTemporalGraph:
    """
    Incremental directed graph maintaining strict historical state.
    Prevents any temporal leakage of future transactions.
    """

    def __init__(self, high_risk_threshold: float = 0.7):
        self.graph = nx.DiGraph()
        self.wallets: Dict[str, WalletHistoricalState] = {}
        self.processed_tx_count = 0
        self.last_processed_timestamp = -1.0
        self.high_risk_threshold = high_risk_threshold
        # Track known flagged/suspicious transactions/wallets historically
        self.flagged_wallets: set = set()

    def _get_or_create_wallet(self, address: str) -> WalletHistoricalState:
        if address not in self.wallets:
            self.wallets[address] = WalletHistoricalState(address=address)
        return self.wallets[address]

    def extract_features_before_update(
        self,
        tx_id: str,
        src_wallet: str,
        dst_wallet: str,
        amount: float,
        timestamp: float,
        assert_chronological: bool = True
    ) -> Dict[str, float]:
        """
        Calculates all temporal, wallet, and topological graph features for a transaction
        STRICTLY based on historical graph state prior to this transaction.
        """
        if assert_chronological and self.last_processed_timestamp > timestamp:
            raise ValueError(
                f"Temporal Leakage Violation: Transaction {tx_id} at timestamp {timestamp} "
                f"is earlier than last processed timestamp {self.last_processed_timestamp}."
            )

        src_state = self.wallets.get(src_wallet, WalletHistoricalState(address=src_wallet))
        dst_state = self.wallets.get(dst_wallet, WalletHistoricalState(address=dst_wallet))

        # --- Source Wallet Historical Features ---
        src_in_degree = src_state.in_tx_count
        src_out_degree = src_state.out_tx_count
        src_total_degree = src_in_degree + src_out_degree
        src_unique_counterparties = len(src_state.counterparties)
        src_counterparty_diversity = (src_unique_counterparties / max(1, src_total_degree))

        src_out_sum = sum(src_state.out_amounts)
        src_out_mean = (src_out_sum / len(src_state.out_amounts)) if src_state.out_amounts else 0.0
        src_out_max = max(src_state.out_amounts) if src_state.out_amounts else 0.0
        src_out_std = float(np.std(src_state.out_amounts)) if len(src_state.out_amounts) > 1 else 0.0

        src_in_sum = sum(src_state.in_amounts)
        src_in_mean = (src_in_sum / len(src_state.in_amounts)) if src_state.in_amounts else 0.0

        src_net_flow = src_in_sum - src_out_sum

        # Temporal delta & velocity for source
        if src_state.tx_count > 0:
            src_time_since_last_tx = max(0.0, timestamp - src_state.last_seen_ts)
            src_wallet_age = max(1.0, timestamp - src_state.first_seen_ts)
            src_tx_velocity_hourly = (src_state.tx_count / (src_wallet_age / 3600.0))
            # Dormant to active transition (> 7 days dormancy: 604800s)
            src_is_dormant_reactivation = 1.0 if src_time_since_last_tx > 604800 else 0.0
        else:
            src_time_since_last_tx = 0.0
            src_wallet_age = 0.0
            src_tx_velocity_hourly = 0.0
            src_is_dormant_reactivation = 0.0

        # Burst / Rolling metrics for source (past 1 hour = 3600s, past 24h = 86400s)
        src_past_1h_txs = 0
        src_past_1h_vol = 0.0
        src_past_24h_txs = 0
        src_past_24h_vol = 0.0
        for t_ts, t_amt in zip(src_state.recent_tx_timestamps, src_state.recent_tx_amounts):
            diff = timestamp - t_ts
            if 0 <= diff <= 3600:
                src_past_1h_txs += 1
                src_past_1h_vol += t_amt
            if 0 <= diff <= 86400:
                src_past_24h_txs += 1
                src_past_24h_vol += t_amt

        # --- Destination Wallet Historical Features ---
        dst_in_degree = dst_state.in_tx_count
        dst_out_degree = dst_state.out_tx_count
        dst_total_degree = dst_in_degree + dst_out_degree
        dst_unique_counterparties = len(dst_state.counterparties)
        dst_in_sum = sum(dst_state.in_amounts)
        dst_in_mean = (dst_in_sum / len(dst_state.in_amounts)) if dst_state.in_amounts else 0.0
        dst_wallet_age = max(0.0, timestamp - dst_state.first_seen_ts) if dst_state.tx_count > 0 else 0.0

        # --- Graph Topological Metrics (from G(t-)) ---
        src_pagerank = 0.0
        src_clustering = 0.0
        local_density = 0.0
        k_hop_suspicious_exposure = 0.0

        if src_wallet in self.graph:
            # Local clustering coefficient in historical undirected projection
            try:
                src_clustering = nx.clustering(self.graph.to_undirected(), src_wallet)
            except Exception:
                src_clustering = 0.0

            # 1-hop and 2-hop neighborhood size
            try:
                neighbors_1hop = set(self.graph.successors(src_wallet)).union(set(self.graph.predecessors(src_wallet)))
                src_1hop_size = len(neighbors_1hop)
                
                # Check suspicious exposure in neighborhood
                suspicious_neighbors = len(neighbors_1hop.intersection(self.flagged_wallets))
                k_hop_suspicious_exposure = suspicious_neighbors / max(1, src_1hop_size)
            except Exception:
                src_1hop_size = 0
                k_hop_suspicious_exposure = 0.0
        else:
            src_1hop_size = 0

        # Rapid transfer sequence indicator (e.g. incoming tx shortly followed by outgoing tx)
        rapid_drain_indicator = 0.0
        if src_state.in_amounts and src_state.last_seen_ts > 0:
            if (timestamp - src_state.last_seen_ts) < 300 and abs(amount - src_state.in_amounts[-1]) < (0.1 * amount + 1e-5):
                rapid_drain_indicator = 1.0

        features = {
            "amount": float(amount),
            "log_amount": float(np.log1p(max(0.0, amount))),
            "src_in_degree": float(src_in_degree),
            "src_out_degree": float(src_out_degree),
            "src_total_degree": float(src_total_degree),
            "src_unique_counterparties": float(src_unique_counterparties),
            "src_counterparty_diversity": float(src_counterparty_diversity),
            "src_out_mean": float(src_out_mean),
            "src_out_max": float(src_out_max),
            "src_out_std": float(src_out_std),
            "src_in_mean": float(src_in_mean),
            "src_net_flow": float(src_net_flow),
            "src_wallet_age_seconds": float(src_wallet_age),
            "src_time_since_last_tx": float(src_time_since_last_tx),
            "src_tx_velocity_hourly": float(src_tx_velocity_hourly),
            "src_is_dormant_reactivation": float(src_is_dormant_reactivation),
            "src_past_1h_txs": float(src_past_1h_txs),
            "src_past_1h_vol": float(src_past_1h_vol),
            "src_past_24h_txs": float(src_past_24h_txs),
            "src_past_24h_vol": float(src_past_24h_vol),
            "dst_in_degree": float(dst_in_degree),
            "dst_out_degree": float(dst_out_degree),
            "dst_total_degree": float(dst_total_degree),
            "dst_unique_counterparties": float(dst_unique_counterparties),
            "dst_in_mean": float(dst_in_mean),
            "dst_wallet_age_seconds": float(dst_wallet_age),
            "src_clustering_coefficient": float(src_clustering),
            "src_1hop_neighborhood_size": float(src_1hop_size),
            "k_hop_suspicious_exposure": float(k_hop_suspicious_exposure),
            "rapid_drain_indicator": float(rapid_drain_indicator),
        }

        return features

    def update_graph(
        self,
        tx_id: str,
        src_wallet: str,
        dst_wallet: str,
        amount: float,
        timestamp: float,
        is_suspicious_lead: bool = False
    ):
        """
        Updates the historical graph state G(t) AFTER features have been extracted.
        """
        src = self._get_or_create_wallet(src_wallet)
        dst = self._get_or_create_wallet(dst_wallet)

        # Update source wallet
        if src.tx_count == 0:
            src.first_seen_ts = timestamp
        src.last_seen_ts = timestamp
        src.tx_count += 1
        src.out_tx_count += 1
        src.out_amounts.append(amount)
        src.counterparties.add(dst_wallet)
        src.out_counterparties.add(dst_wallet)
        src.recent_tx_timestamps.append(timestamp)
        src.recent_tx_amounts.append(amount)

        # Prune recent transactions older than 24h from rolling buffer to keep memory efficient
        cutoff = timestamp - 86400
        while src.recent_tx_timestamps and src.recent_tx_timestamps[0] < cutoff:
            src.recent_tx_timestamps.pop(0)
            src.recent_tx_amounts.pop(0)

        # Update destination wallet
        if dst.tx_count == 0:
            dst.first_seen_ts = timestamp
        dst.last_seen_ts = timestamp
        dst.tx_count += 1
        dst.in_tx_count += 1
        dst.in_amounts.append(amount)
        dst.counterparties.add(src_wallet)
        dst.in_counterparties.add(src_wallet)

        # Update networkx graph
        if self.graph.has_edge(src_wallet, dst_wallet):
            self.graph[src_wallet][dst_wallet]["weight"] += amount
            self.graph[src_wallet][dst_wallet]["count"] += 1
        else:
            self.graph.add_edge(src_wallet, dst_wallet, weight=amount, count=1, first_tx_ts=timestamp)

        if is_suspicious_lead:
            self.flagged_wallets.add(src_wallet)
            self.flagged_wallets.add(dst_wallet)

        self.processed_tx_count += 1
        self.last_processed_timestamp = max(self.last_processed_timestamp, timestamp)

    def process_transaction_stream(
        self,
        transactions: List[Dict[str, Any]],
        flagged_threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Processes a full chronological stream of transactions with guaranteed anti-leakage.
        Returns list of transaction dicts enriched with extracted features.
        """
        # Ensure chronological ordering
        sorted_txs = sorted(transactions, key=lambda x: float(x.get("timestamp", 0)))
        enriched = []

        for tx in sorted_txs:
            tx_id = str(tx.get("transaction_id") or tx.get("tx_id") or f"tx_{len(enriched)}")
            src = str(tx.get("source_wallet") or tx.get("src") or tx.get("source"))
            dst = str(tx.get("destination_wallet") or tx.get("dst") or tx.get("destination"))
            amt = float(tx.get("amount", 0.0))
            ts = float(tx.get("timestamp", 0.0))

            # 1. Extract features using G(t-)
            feats = self.extract_features_before_update(
                tx_id=tx_id,
                src_wallet=src,
                dst_wallet=dst,
                amount=amt,
                timestamp=ts,
                assert_chronological=True
            )

            tx_copy = dict(tx)
            tx_copy["features"] = feats
            enriched.append(tx_copy)

            # 2. Update graph state G(t)
            is_flagged = bool(tx.get("label", 0) == 1 or tx.get("risk_score", 0) >= flagged_threshold)
            self.update_graph(
                tx_id=tx_id,
                src_wallet=src,
                dst_wallet=dst,
                amount=amt,
                timestamp=ts,
                is_suspicious_lead=is_flagged
            )

        return enriched
