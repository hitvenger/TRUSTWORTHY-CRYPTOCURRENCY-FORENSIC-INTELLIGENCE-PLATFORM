"""
Pydantic Schemas for Custody, Analyst Reviews, Reports, and Integrity.
"""

from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import datetime


class CustodyEventResponse(BaseModel):
    event_id: str
    case_id: str
    evidence_id: Optional[str]
    actor: str
    role: str
    action: str
    timestamp: str
    metadata_json: Dict[str, Any]
    previous_hash: str
    event_hash: str

    class Config:
        from_attributes = True


class AnalystReviewCreate(BaseModel):
    case_id: str
    evidence_id: str
    new_state: str  # FORENSIC_FINDING, REJECTED, ESCALATED, UNDER_REVIEW
    finding_summary: str
    rationale: str
    corroborating_notes: Optional[str] = ""


class AnalystReviewResponse(BaseModel):
    review_id: str
    case_id: str
    evidence_id: str
    transaction_id: Optional[str]
    analyst_name: str
    role: str
    prior_state: str
    new_state: str
    finding_summary: str
    rationale: str
    corroborating_notes: Optional[str]
    created_at: Optional[datetime.datetime]

    class Config:
        from_attributes = True


class EvidenceTamperRequest(BaseModel):
    field_to_modify: str  # amount, risk_score, source_wallet, etc.
    new_value: Any


class BlockchainAnchorRequest(BaseModel):
    evidence_id: str
    submitter: Optional[str] = "0x71C...ForensicLead"


class ReportGenerateRequest(BaseModel):
    case_id: str
    report_title: Optional[str] = "Forensic Examination Report"
    investigator_name: Optional[str] = "Lead Forensic Analyst"
    include_chain_of_custody: bool = True
    include_shap_explanations: bool = True
    include_blockchain_anchors: bool = True
