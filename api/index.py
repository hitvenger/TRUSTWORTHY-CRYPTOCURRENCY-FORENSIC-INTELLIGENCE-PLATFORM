"""
TCF-FX Vercel Serverless API — Lightweight Edge Function.

Serves the forensic intelligence API with demo data on Vercel's serverless
infrastructure. The full ML pipeline (scikit-learn, SHAP, XGBoost, PyTorch)
runs locally; this edge function provides the REST API layer for the
deployed React dashboard.
"""

import sys
import os
import time
import hashlib
import json
import uuid
import random
import math
from datetime import datetime, timezone

# Add root project path to sys.path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel
from typing import Dict, Any, List, Optional

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = FastAPI(
    title="TCF-FX Forensic Intelligence Platform API",
    description="Evidence-aware AI for explainable cryptocurrency digital forensics.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Deterministic demo data seeded from the same constants as the full engine
# ---------------------------------------------------------------------------

random.seed(42)

DEMO_CASE = {
    "case_id": "case_operation_shadowchain",
    "title": "Operation ShadowChain — Illicit Layering & Mixer Investigation",
    "description": "Forensic investigation into peeling chains, high-velocity mixer pooling, and rapid asset drains.",
    "investigator": "Special Agent Vance",
    "status": "ACTIVE",
    "priority": "CRITICAL",
    "tags": ["RANSOMWARE", "PEELING_CHAIN", "MIXER", "TRIAGE_PRIORITY_1"],
    "created_at": "2026-01-15T08:30:00Z",
}

WALLET_POOL = [
    "0xa1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0",
    "0xdeadbeef1234567890abcdef1234567890abcdef",
    "0x742d35Cc6634C0532925a3b844Bc9e7595f2bD18",
    "0xMixerPool_TornadoCash_001_DepositRelay_v3",
    "0xPeelingChain_Hop7_Intermediate_Disposable",
    "0xExchangeDeposit_Binance_HotWallet_0x91f3",
    "0xRansomwareExtortion_LockBit3_Payout_Addr",
    "0xCleanWallet_LegitBusiness_Payroll_0xc7d2",
]


def _make_digest(data: dict) -> str:
    """Deterministic SHA-256 digest matching the full forensic engine canonical format."""
    filtered = {k: v for k, v in sorted(data.items()) if k != "integrity_digest"}
    raw = json.dumps(filtered, separators=(",", ":"), sort_keys=True)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _generate_demo_evidence(n: int = 20) -> List[Dict[str, Any]]:
    rng = random.Random(42)
    evidence = []
    base_ts = 1704067200.0  # 2024-01-01T00:00:00Z
    for i in range(n):
        amount = round(rng.uniform(0.001, 50.0), 8)
        risk = round(rng.uniform(0.05, 0.98), 4)
        conf = round(1.0 - rng.uniform(0.01, 0.15), 4)
        delta = round(rng.uniform(0.01, 0.12), 4)
        ts = base_ts + i * 3600 + rng.randint(0, 1800)
        src = rng.choice(WALLET_POOL)
        dst = rng.choice([w for w in WALLET_POOL if w != src])
        tx_id = f"tx_{uuid.UUID(int=rng.getrandbits(128)).hex[:16]}"
        ev_id = f"ev_{uuid.UUID(int=rng.getrandbits(128)).hex[:16]}"

        rec = {
            "evidence_id": ev_id,
            "case_id": "case_operation_shadowchain",
            "transaction_id": tx_id,
            "source_wallet": src,
            "destination_wallet": dst,
            "amount": amount,
            "risk_score": risk,
            "confidence": conf,
            "uncertainty_delta": delta,
            "event_timestamp": ts,
            "model_version": "1.0.0",
            "analyst_status": rng.choice(["MODEL_LEAD", "FORENSIC_FINDING", "MODEL_LEAD", "MODEL_LEAD"]),
            "is_tampered": False,
            "is_anchored": rng.random() > 0.6,
            "explanation": f"Top SHAP drivers: src_tx_velocity_hourly (+{round(rng.uniform(0.1, 0.5), 4)}), "
                           f"rapid_drain_indicator (+{round(rng.uniform(0.05, 0.3), 4)}), "
                           f"amount (-{round(rng.uniform(0.01, 0.1), 4)})",
        }
        rec["integrity_digest"] = _make_digest(rec)
        evidence.append(rec)
    return evidence


DEMO_EVIDENCE = _generate_demo_evidence(20)

# ---------------------------------------------------------------------------
# Middleware
# ---------------------------------------------------------------------------


@app.middleware("http")
async def timing_middleware(request: Request, call_next):
    start = time.time()
    try:
        response = await call_next(request)
    except Exception as exc:
        return JSONResponse(status_code=500, content={"error": str(exc)})
    response.headers["X-Process-Time-Sec"] = f"{time.time() - start:.4f}"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    return response


# ---------------------------------------------------------------------------
# Routes — Root / Health / Favicon
# ---------------------------------------------------------------------------


@app.get("/favicon.ico")
def favicon():
    return Response(status_code=204)


@app.get("/")
def root():
    return {
        "platform": "TCF-FX — Trustworthy Cryptocurrency Forensic Intelligence Platform",
        "status": "ONLINE",
        "version": "1.0.0",
        "deployment": "vercel-serverless",
        "docs": "/docs",
        "health": "/health",
        "api_v1": "/api/v1",
        "axiom": "AI Output != Forensic Finding != Legal Conclusion",
    }


@app.get("/health")
def health():
    return {
        "status": "HEALTHY",
        "service": "TCF-FX Forensic Backend",
        "version": "1.0.0",
        "deployment": "vercel-edge",
        "trust_dimensions": [
            "Evidence Trust",
            "Analytical Trust",
            "Explanatory Trust",
            "Governance Trust",
            "Legal Trust",
        ],
    }


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

import jwt as pyjwt

SECRET_KEY = os.getenv("SECRET_KEY", "tcf_fx_super_secret_forensic_key_2026_salt_9981")
ALGORITHM = "HS256"

DEMO_USERS = {
    "admin": {"password": "admin", "role": "ADMIN", "name": "Platform Administrator"},
    "investigator": {"password": "investigator", "role": "INVESTIGATOR", "name": "Special Agent Vance"},
    "analyst": {"password": "analyst", "role": "ANALYST", "name": "Forensic Analyst Chen"},
    "auditor": {"password": "auditor", "role": "AUDITOR", "name": "Compliance Auditor Kim"},
}


class LoginRequest(BaseModel):
    username: str
    password: str


@app.post("/api/v1/auth/login")
def login(req: LoginRequest):
    user = DEMO_USERS.get(req.username)
    if not user or user["password"] != req.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = pyjwt.encode(
        {"sub": req.username, "role": user["role"], "name": user["name"]},
        SECRET_KEY,
        algorithm=ALGORITHM,
    )
    return {"access_token": token, "token_type": "bearer", "role": user["role"]}


def get_current_user(request: Request) -> Dict[str, Any]:
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return {"sub": "anonymous", "role": "VIEWER", "name": "Anonymous"}
    try:
        payload = pyjwt.decode(auth.split(" ")[1], SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except Exception:
        return {"sub": "anonymous", "role": "VIEWER", "name": "Anonymous"}


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------


@app.get("/api/v1/dashboard/summary")
def dashboard_summary(user: Dict = Depends(get_current_user)):
    high_risk = [e for e in DEMO_EVIDENCE if e["risk_score"] >= 0.65]
    critical = [e for e in DEMO_EVIDENCE if e["risk_score"] >= 0.80]
    findings = [e for e in DEMO_EVIDENCE if e["analyst_status"] == "FORENSIC_FINDING"]
    anchored = [e for e in DEMO_EVIDENCE if e["is_anchored"]]
    return {
        "metrics": {
            "open_cases": 1,
            "total_evidence": len(DEMO_EVIDENCE),
            "high_risk_leads": len(high_risk),
            "critical_leads": len(critical),
            "integrity_tamper_alerts": 0,
            "analyst_review_queue": len([e for e in DEMO_EVIDENCE if e["analyst_status"] == "MODEL_LEAD" and e["risk_score"] >= 0.60]),
            "total_custody_events": len(DEMO_EVIDENCE) * 3,
            "confirmed_findings": len(findings),
            "anchored_on_chain": len(anchored),
        },
        "risk_distribution": {
            "low": len([e for e in DEMO_EVIDENCE if e["risk_score"] < 0.35]),
            "medium": len([e for e in DEMO_EVIDENCE if 0.35 <= e["risk_score"] < 0.60]),
            "high": len([e for e in DEMO_EVIDENCE if 0.60 <= e["risk_score"] < 0.80]),
            "critical": len(critical),
        },
        "recent_leads": [
            {
                "evidence_id": e["evidence_id"],
                "case_id": e["case_id"],
                "transaction_id": e["transaction_id"],
                "amount": e["amount"],
                "risk_score": e["risk_score"],
                "confidence": e["confidence"],
                "uncertainty_delta": e["uncertainty_delta"],
                "analyst_status": e["analyst_status"],
                "is_tampered": e["is_tampered"],
                "is_anchored": e["is_anchored"],
                "timestamp": e["event_timestamp"],
            }
            for e in sorted(DEMO_EVIDENCE, key=lambda x: x["event_timestamp"], reverse=True)[:8]
        ],
    }


# ---------------------------------------------------------------------------
# Cases
# ---------------------------------------------------------------------------


@app.get("/api/v1/cases")
def list_cases(user: Dict = Depends(get_current_user)):
    return [DEMO_CASE]


@app.post("/api/v1/cases")
def create_case(request: Request, user: Dict = Depends(get_current_user)):
    return DEMO_CASE


@app.get("/api/v1/cases/{case_id}")
def get_case(case_id: str, user: Dict = Depends(get_current_user)):
    return DEMO_CASE


# ---------------------------------------------------------------------------
# Evidence
# ---------------------------------------------------------------------------


@app.get("/api/v1/evidence")
def list_evidence(user: Dict = Depends(get_current_user)):
    return DEMO_EVIDENCE


@app.get("/api/v1/evidence/{evidence_id}")
def get_evidence(evidence_id: str, user: Dict = Depends(get_current_user)):
    for e in DEMO_EVIDENCE:
        if e["evidence_id"] == evidence_id:
            return e
    raise HTTPException(status_code=404, detail="Evidence not found")


@app.get("/api/v1/evidence/{evidence_id}/verify")
def verify_evidence(evidence_id: str, user: Dict = Depends(get_current_user)):
    for e in DEMO_EVIDENCE:
        if e["evidence_id"] == evidence_id:
            recomputed = _make_digest(e)
            return {
                "evidence_id": evidence_id,
                "stored_digest": e["integrity_digest"],
                "recomputed_digest": recomputed,
                "integrity_verified": e["integrity_digest"] == recomputed,
                "tamper_detected": e["integrity_digest"] != recomputed,
            }
    raise HTTPException(status_code=404, detail="Evidence not found")


# ---------------------------------------------------------------------------
# Transactions
# ---------------------------------------------------------------------------


@app.get("/api/v1/transactions")
def list_transactions(user: Dict = Depends(get_current_user)):
    return [
        {
            "transaction_id": e["transaction_id"],
            "source_wallet": e["source_wallet"],
            "destination_wallet": e["destination_wallet"],
            "amount": e["amount"],
            "timestamp": e["event_timestamp"],
            "risk_score": e["risk_score"],
        }
        for e in DEMO_EVIDENCE
    ]


# ---------------------------------------------------------------------------
# Graph
# ---------------------------------------------------------------------------


@app.get("/api/v1/graph/nodes")
def graph_nodes(user: Dict = Depends(get_current_user)):
    wallets = set()
    for e in DEMO_EVIDENCE:
        wallets.add(e["source_wallet"])
        wallets.add(e["destination_wallet"])
    nodes = []
    for i, w in enumerate(wallets):
        txs = [e for e in DEMO_EVIDENCE if e["source_wallet"] == w or e["destination_wallet"] == w]
        avg_risk = sum(e["risk_score"] for e in txs) / max(len(txs), 1)
        nodes.append({
            "id": w,
            "label": w[:10] + "...",
            "risk_score": round(avg_risk, 4),
            "transaction_count": len(txs),
            "x": 100 + (i % 5) * 200,
            "y": 100 + (i // 5) * 150,
        })
    edges = [
        {
            "source": e["source_wallet"],
            "target": e["destination_wallet"],
            "amount": e["amount"],
            "risk_score": e["risk_score"],
        }
        for e in DEMO_EVIDENCE
    ]
    return {"nodes": nodes, "edges": edges}


# ---------------------------------------------------------------------------
# Blockchain
# ---------------------------------------------------------------------------


@app.get("/api/v1/blockchain/anchored")
def blockchain_anchored(user: Dict = Depends(get_current_user)):
    return [
        {
            "evidence_id": e["evidence_id"],
            "digest": e["integrity_digest"],
            "anchored_at": e["event_timestamp"],
            "tx_hash": f"0x{hashlib.sha256(e['evidence_id'].encode()).hexdigest()[:64]}",
        }
        for e in DEMO_EVIDENCE
        if e["is_anchored"]
    ]


# ---------------------------------------------------------------------------
# Chain of Custody
# ---------------------------------------------------------------------------


@app.get("/api/v1/custody/{evidence_id}")
def custody_chain(evidence_id: str, user: Dict = Depends(get_current_user)):
    actions = ["ACQUISITION", "AI_ANALYSIS", "INTEGRITY_SEALED"]
    chain = []
    prev_hash = "0" * 64
    for i, action in enumerate(actions):
        event = {
            "event_index": i,
            "evidence_id": evidence_id,
            "action": action,
            "actor": "Special Agent Vance",
            "role": "INVESTIGATOR",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "previous_hash": prev_hash,
        }
        current_hash = hashlib.sha256(json.dumps(event, sort_keys=True).encode()).hexdigest()
        event["event_hash"] = current_hash
        chain.append(event)
        prev_hash = current_hash
    return chain


# ---------------------------------------------------------------------------
# Audit
# ---------------------------------------------------------------------------


@app.get("/api/v1/audit/log")
def audit_log(user: Dict = Depends(get_current_user)):
    return [
        {"timestamp": datetime.now(timezone.utc).isoformat(), "actor": "Agent Vance", "action": "CASE_CREATED", "detail": "Created Operation ShadowChain"},
        {"timestamp": datetime.now(timezone.utc).isoformat(), "actor": "Agent Vance", "action": "EVIDENCE_INGESTED", "detail": f"{len(DEMO_EVIDENCE)} transaction evidence items ingested"},
        {"timestamp": datetime.now(timezone.utc).isoformat(), "actor": "System", "action": "AI_ANALYSIS_COMPLETE", "detail": "Multi-model risk scoring completed"},
        {"timestamp": datetime.now(timezone.utc).isoformat(), "actor": "System", "action": "SHAP_ATTRIBUTIONS_BOUND", "detail": "SHAP explanations bound to evidence records"},
        {"timestamp": datetime.now(timezone.utc).isoformat(), "actor": "Auditor Kim", "action": "AUDIT_REVIEW", "detail": "Custody chain integrity verified"},
    ]


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------


@app.get("/api/v1/models")
def list_models(user: Dict = Depends(get_current_user)):
    return [
        {"model_id": "model_rf_baseline", "name": "Forensic Random Forest", "version": "1.0.0", "type": "supervised", "n_estimators": 250, "max_depth": 12, "status": "ACTIVE"},
        {"model_id": "model_isolation_forest", "name": "Forensic Isolation Forest", "version": "1.0.0", "type": "unsupervised", "n_estimators": 150, "contamination": 0.08, "status": "ACTIVE"},
        {"model_id": "model_xgboost_tabular", "name": "Forensic Gradient Boosting", "version": "1.0.0", "type": "supervised", "n_estimators": 200, "max_depth": 6, "status": "ACTIVE"},
        {"model_id": "model_graphsage_relational", "name": "GraphSAGE Relational", "version": "1.0.0", "type": "relational", "hidden_dim": 32, "epochs": 40, "status": "EXPERIMENTAL"},
    ]


# ---------------------------------------------------------------------------
# Reports
# ---------------------------------------------------------------------------


@app.get("/api/v1/reports")
def list_reports(user: Dict = Depends(get_current_user)):
    return [
        {"report_id": "rpt_001", "case_id": "case_operation_shadowchain", "format": "PDF", "title": "Forensic Examination Dossier — Operation ShadowChain", "created_at": datetime.now(timezone.utc).isoformat()},
        {"report_id": "rpt_002", "case_id": "case_operation_shadowchain", "format": "JSON", "title": "Machine-Readable Evidence Manifest", "created_at": datetime.now(timezone.utc).isoformat()},
    ]


# ---------------------------------------------------------------------------
# Analyst Review
# ---------------------------------------------------------------------------


@app.get("/api/v1/analyst-reviews")
def list_reviews(user: Dict = Depends(get_current_user)):
    findings = [e for e in DEMO_EVIDENCE if e["analyst_status"] == "FORENSIC_FINDING"]
    return [
        {
            "evidence_id": e["evidence_id"],
            "previous_state": "MODEL_LEAD",
            "new_state": "FORENSIC_FINDING",
            "rationale": "Confirmed illicit layering pattern via topological analysis and SHAP attribution review.",
            "analyst": "Forensic Analyst Chen",
            "reviewed_at": datetime.now(timezone.utc).isoformat(),
        }
        for e in findings
    ]


# ---------------------------------------------------------------------------
# Experiments
# ---------------------------------------------------------------------------


@app.get("/api/v1/experiments/benchmarks")
def benchmarks(user: Dict = Depends(get_current_user)):
    return {
        "seeds": [7, 19, 31, 43, 59],
        "split": "chronological_70_30",
        "results": [
            {"model": "Random Forest (Baseline)", "precision": 0.8920, "recall": 0.8760, "f1": 0.8838, "roc_auc": 0.9416, "pr_auc": 0.8912, "brier": 0.0524, "latency_ms": 0.324},
            {"model": "XGBoost (HistGradient)", "precision": 0.8890, "recall": 0.8735, "f1": 0.8812, "roc_auc": 0.9398, "pr_auc": 0.8876, "brier": 0.0541, "latency_ms": 0.412},
            {"model": "Isolation Forest (Unsupervised)", "precision": 0.7650, "recall": 0.7240, "f1": 0.7439, "roc_auc": 0.8410, "pr_auc": 0.7650, "brier": 0.1120, "latency_ms": 0.285},
            {"model": "GraphSAGE (Relational)", "precision": 0.8420, "recall": 0.8210, "f1": 0.8314, "roc_auc": 0.8990, "pr_auc": 0.8410, "brier": 0.0782, "latency_ms": 1.840},
            {"model": "Full TCF-FX Multi-Fusion", "precision": 0.8920, "recall": 0.8760, "f1": 0.8838, "roc_auc": 0.9416, "pr_auc": 0.8912, "brier": 0.0524, "latency_ms": 0.324},
        ],
    }
