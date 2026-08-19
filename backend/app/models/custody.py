"""
SQLAlchemy Models for Custody, Reviews, Model Cards, Auditing and Users.
"""

from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
import datetime
from backend.app.core.database import Base


class CustodyEvent(Base):
    __tablename__ = "custody_events"

    event_id = Column(String(64), primary_key=True, index=True)
    case_id = Column(String(64), ForeignKey("cases.case_id"), nullable=False, index=True)
    evidence_id = Column(String(64), nullable=True, index=True)
    actor = Column(String(128), nullable=False)
    role = Column(String(64), nullable=False)
    action = Column(String(64), nullable=False)
    timestamp = Column(String(64), nullable=False)
    metadata_json = Column(JSON, default=dict)
    previous_hash = Column(String(64), nullable=False)
    event_hash = Column(String(64), nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    case = relationship("Case", back_populates="custody_events")


class AnalystReview(Base):
    __tablename__ = "analyst_reviews"

    review_id = Column(String(64), primary_key=True, index=True)
    case_id = Column(String(64), nullable=False, index=True)
    evidence_id = Column(String(64), nullable=False, index=True)
    transaction_id = Column(String(128), nullable=True)
    analyst_name = Column(String(128), nullable=False)
    role = Column(String(64), default="ANALYST")
    prior_state = Column(String(32), default="MODEL_LEAD")
    new_state = Column(String(32), nullable=False)  # FORENSIC_FINDING, REJECTED, ESCALATED, etc.
    finding_summary = Column(Text, nullable=False)
    rationale = Column(Text, nullable=False)
    corroborating_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class ModelRegistry(Base):
    __tablename__ = "model_registry"

    model_id = Column(String(64), primary_key=True, index=True)
    name = Column(String(128), nullable=False)
    version = Column(String(32), nullable=False)
    model_type = Column(String(64), nullable=False)  # SUPERVISED_RF, UNSUPERVISED_IFOREST, XGBOOST, GNN
    parameters_json = Column(JSON, default=dict)
    metrics_json = Column(JSON, default=dict)
    model_card_json = Column(JSON, default=dict)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    log_id = Column(String(64), primary_key=True, index=True)
    user_id = Column(String(64), nullable=False)
    action = Column(String(64), nullable=False)
    resource_type = Column(String(64), nullable=False)
    resource_id = Column(String(128), nullable=True)
    ip_address = Column(String(64), default="127.0.0.1")
    timestamp = Column(String(64), nullable=False)
    details_json = Column(JSON, default=dict)


class User(Base):
    __tablename__ = "users"

    id = Column(String(64), primary_key=True, index=True)
    username = Column(String(64), unique=True, index=True, nullable=False)
    email = Column(String(128), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(32), default="INVESTIGATOR")  # ADMIN, INVESTIGATOR, ANALYST, AUDITOR, VIEWER
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
