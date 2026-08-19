"""
Investigation Graph and Wallet Profiling API Endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional

from backend.app.core.database import get_db
from backend.app.core.security import get_current_user
from backend.app.models.case import Evidence, Case
from backend.app.services.evidence_service import ForensicPipelineRuntime

router = APIRouter(tags=["Graph & Wallets"])


@router.get("/graph/explore")
def explore_investigation_graph(
    case_id: Optional[str] = None,
    min_risk: float = 0.0,
    limit: int = 250,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Returns nodes (wallets) and edges (transactions) for interactive topological visualization.
    """
    query = db.query(Evidence)
    if case_id:
        query = query.filter(Evidence.case_id == case_id)
    if min_risk > 0:
        query = query.filter(Evidence.risk_score >= min_risk)
        
    items = query.limit(limit).all()

    nodes_map: Dict[str, Dict[str, Any]] = {}
    edges_list = []

    for ev in items:
        src = ev.source_wallet
        dst = ev.destination_wallet

        # Process Source Node
        if src not in nodes_map:
            nodes_map[src] = {
                "id": src,
                "label": src[:8] + "...",
                "full_address": src,
                "type": "wallet",
                "in_txs": 0,
                "out_txs": 0,
                "total_volume": 0.0,
                "max_risk": 0.0,
                "is_flagged": False
            }
        nodes_map[src]["out_txs"] += 1
        nodes_map[src]["total_volume"] += ev.amount
        nodes_map[src]["max_risk"] = max(nodes_map[src]["max_risk"], ev.risk_score)
        if ev.risk_score >= 0.65:
            nodes_map[src]["is_flagged"] = True

        # Process Destination Node
        if dst not in nodes_map:
            nodes_map[dst] = {
                "id": dst,
                "label": dst[:8] + "...",
                "full_address": dst,
                "type": "wallet",
                "in_txs": 0,
                "out_txs": 0,
                "total_volume": 0.0,
                "max_risk": 0.0,
                "is_flagged": False
            }
        nodes_map[dst]["in_txs"] += 1
        nodes_map[dst]["total_volume"] += ev.amount
        nodes_map[dst]["max_risk"] = max(nodes_map[dst]["max_risk"], ev.risk_score)
        if ev.risk_score >= 0.65:
            nodes_map[dst]["is_flagged"] = True

        # Edge
        edges_list.append({
            "id": f"edge_{ev.evidence_id}",
            "source": src,
            "target": dst,
            "transaction_id": ev.transaction_id,
            "evidence_id": ev.evidence_id,
            "amount": ev.amount,
            "risk_score": ev.risk_score,
            "confidence": ev.confidence,
            "timestamp": ev.event_timestamp or ev.acquisition_timestamp,
            "analyst_status": ev.analyst_status,
            "is_tampered": ev.is_tampered,
        })

    return {
        "nodes": list(nodes_map.values()),
        "edges": edges_list,
        "total_nodes": len(nodes_map),
        "total_edges": len(edges_list),
    }


@router.get("/wallets/{wallet_address}")
def get_wallet_profile(
    wallet_address: str,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    in_txs = db.query(Evidence).filter(Evidence.destination_wallet == wallet_address).all()
    out_txs = db.query(Evidence).filter(Evidence.source_wallet == wallet_address).all()
    
    if not in_txs and not out_txs:
        # Check runtime graph state
        runtime = ForensicPipelineRuntime.get_instance()
        state = runtime.graph_engine.wallets.get(wallet_address)
        if not state:
            raise HTTPException(status_code=404, detail="Wallet not found in active graph records")
        return {
            "address": wallet_address,
            "transaction_count": state.tx_count,
            "inbound_count": state.in_tx_count,
            "outbound_count": state.out_tx_count,
            "unique_counterparties": len(state.counterparties),
            "recent_activity_count": len(state.recent_tx_timestamps)
        }

    total_in = sum(t.amount for t in in_txs)
    total_out = sum(t.amount for t in out_txs)
    max_risk = max([t.risk_score for t in in_txs + out_txs] or [0.0])
    
    counterparties = set([t.source_wallet for t in in_txs] + [t.destination_wallet for t in out_txs])

    return {
        "address": wallet_address,
        "transaction_count": len(in_txs) + len(out_txs),
        "inbound_count": len(in_txs),
        "outbound_count": len(out_txs),
        "total_received": round(total_in, 4),
        "total_sent": round(total_out, 4),
        "net_balance_estimate": round(total_in - total_out, 4),
        "max_risk_score": round(max_risk, 4),
        "risk_level": "CRITICAL" if max_risk >= 0.8 else ("HIGH" if max_risk >= 0.6 else ("MEDIUM" if max_risk >= 0.35 else "LOW")),
        "unique_counterparty_count": len(counterparties),
        "recent_transactions": [
            {
                "evidence_id": t.evidence_id,
                "transaction_id": t.transaction_id,
                "counterparty": t.destination_wallet if t.source_wallet == wallet_address else t.source_wallet,
                "direction": "OUTBOUND" if t.source_wallet == wallet_address else "INBOUND",
                "amount": t.amount,
                "risk_score": t.risk_score,
                "status": t.analyst_status,
            }
            for t in (out_txs + in_txs)[:20]
        ]
    }
