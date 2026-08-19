"""
Blockchain Smart Contract Evidence Anchor Registry API Endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any, Optional

from backend.app.core.security import get_current_user
from blockchain.client import BlockchainAnchorClient

router = APIRouter(prefix="/blockchain", tags=["Blockchain Evidence Anchor"])
anchor_client = BlockchainAnchorClient()


@router.get("/anchors", response_model=List[Dict[str, Any]])
def list_anchors(current_user: Dict[str, Any] = Depends(get_current_user)):
    return anchor_client.list_anchors()


@router.get("/verify/{evidence_id}")
def verify_anchor(
    evidence_id: str,
    candidate_digest: Optional[str] = None,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    res = anchor_client.verify_evidence(evidence_id, candidate_digest=candidate_digest)
    return res


@router.get("/network-status")
def get_network_status(current_user: Dict[str, Any] = Depends(get_current_user)):
    return {
        "network": anchor_client.network_name,
        "block_height": anchor_client.block_height,
        "total_anchors_recorded": len(anchor_client.simulated_ledger),
        "consensus": "EVM Proof-of-Authority / Simulated Local Node",
        "status": "OPERATIONAL"
    }
