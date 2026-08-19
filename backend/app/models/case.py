"""
SQLAlchemy Models for Cases and Digital Evidence.
"""

from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
import datetime
from backend.app.core.database import Base


class Case(Base):
    __tablename__ = "cases"

    case_id = Column(String(64), primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    investigator = Column(String(128), nullable=False, default="Lead Investigator")
    status = Column(String(32), default="ACTIVE")  # ACTIVE, UNDER_REVIEW, CLOSED, ARCHIVED
    priority = Column(String(32), default="HIGH")  # LOW, MEDIUM, HIGH, CRITICAL
    tags = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    evidence_items = relationship("Evidence", back_populates="case", cascade="all, delete-orphan")
    custody_events = relationship("CustodyEvent", back_populates="case", cascade="all, delete-orphan")


class Evidence(Base):
    __tablename__ = "evidence"

    evidence_id = Column(String(64), primary_key=True, index=True)
    case_id = Column(String(64), ForeignKey("cases.case_id"), nullable=False, index=True)
    evidence_type = Column(String(64), default="CRYPTOCURRENCY_TRANSACTION")
    source = Column(String(128), default="BLOCKCHAIN_LEDGER")
    source_identifier = Column(String(255), nullable=True)
    acquisition_timestamp = Column(String(64), nullable=False)
    event_timestamp = Column(String(64), nullable=True)
    transaction_id = Column(String(128), index=True)
    source_wallet = Column(String(128), index=True)
    destination_wallet = Column(String(128), index=True)
    amount = Column(Float, default=0.0)
    
    # Forensic AI & Uncertainty Metrics
    feature_schema_version = Column(String(32), default="1.0.0")
    model_id = Column(String(64), default="model_rf_baseline")
    model_version = Column(String(32), default="1.0.0")
    risk_score = Column(Float, default=0.0)
    anomaly_score = Column(Float, default=0.0)
    graph_score = Column(Float, default=0.0)
    temporal_score = Column(Float, default=0.0)
    confidence = Column(String(32), default="MEDIUM")
    uncertainty_delta = Column(Float, default=0.05)
    
    # Explainability & Corroboration
    explanation_json = Column(JSON, default=dict)
    corroboration_json = Column(JSON, default=dict)
    features_json = Column(JSON, default=dict)
    
    # Review & Findings
    analyst_status = Column(String(32), default="MODEL_LEAD")  # MODEL_LEAD, UNDER_REVIEW, FORENSIC_FINDING, REJECTED, ESCALATED
    analyst_comment = Column(Text, nullable=True)
    analyst_name = Column(String(128), nullable=True)
    
    # Cryptographic Integrity & Blockchain Anchor
    integrity_digest = Column(String(64), nullable=False)
    is_tampered = Column(Boolean, default=False)
    blockchain_tx_hash = Column(String(128), nullable=True)
    blockchain_block = Column(Integer, nullable=True)
    is_anchored = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    case = relationship("Case", back_populates="evidence_items")
