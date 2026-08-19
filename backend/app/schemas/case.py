"""
Pydantic Schemas for Forensic Cases, Evidence, and Transactions.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import datetime


class CaseCreate(BaseModel):
    title: str
    description: Optional[str] = ""
    investigator: Optional[str] = "Lead Investigator"
    priority: Optional[str] = "HIGH"
    tags: Optional[List[str]] = []


class CaseResponse(BaseModel):
    case_id: str
    title: str
    description: Optional[str]
    investigator: str
    status: str
    priority: str
    tags: List[str]
    evidence_count: Optional[int] = 0
    created_at: Optional[datetime.datetime]
    updated_at: Optional[datetime.datetime]

    class Config:
        from_attributes = True


class EvidenceCreate(BaseModel):
    case_id: str
    transaction_id: str
    source_wallet: str
    destination_wallet: str
    amount: float
    timestamp: float
    source: Optional[str] = "BLOCKCHAIN_INGESTION"
    source_identifier: Optional[str] = "ETHEREUM_MAINNET_NODE_01"
    evidence_type: Optional[str] = "CRYPTOCURRENCY_TRANSACTION"


class EvidenceResponse(BaseModel):
    evidence_id: str
    case_id: str
    evidence_type: str
    source: str
    source_identifier: Optional[str]
    acquisition_timestamp: str
    event_timestamp: Optional[str]
    transaction_id: str
    source_wallet: str
    destination_wallet: str
    amount: float
    feature_schema_version: str
    model_id: str
    model_version: str
    risk_score: float
    anomaly_score: float
    graph_score: float
    temporal_score: float
    confidence: str
    uncertainty_delta: float
    explanation_json: Dict[str, Any]
    corroboration_json: Dict[str, Any]
    features_json: Dict[str, Any]
    analyst_status: str
    analyst_comment: Optional[str]
    analyst_name: Optional[str]
    integrity_digest: str
    is_tampered: bool
    blockchain_tx_hash: Optional[str]
    blockchain_block: Optional[int]
    is_anchored: bool
    created_at: Optional[datetime.datetime]

    class Config:
        from_attributes = True


class TransactionAnalysisRequest(BaseModel):
    case_id: Optional[str] = "case_default"
    transaction_id: str
    source_wallet: str
    destination_wallet: str
    amount: float
    timestamp: float
    source_identifier: Optional[str] = "LIVE_FORENSIC_STREAM"


class BatchAnalysisRequest(BaseModel):
    case_id: str
    transactions: List[TransactionAnalysisRequest]
