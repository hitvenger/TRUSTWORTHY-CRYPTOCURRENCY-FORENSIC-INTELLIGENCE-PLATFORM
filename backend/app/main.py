"""
TCF-FX — Trustworthy Cryptocurrency Forensic Intelligence Platform
Main FastAPI Backend Application Entrypoint.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time

from backend.app.core.config import settings
from backend.app.core.database import engine, Base
import backend.app.models  # Import all models to ensure schema binding
from backend.app.api.v1 import cases, evidence, transactions, analyst_review, reports, models, experiments, dashboard, graph, blockchain, audit, auth

# Initialize tables
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"[!] Warning during table creation: {e}")

app = FastAPI(
    title="TCF-FX Forensic Intelligence Platform API",
    description="Evidence-aware AI for explainable cryptocurrency digital forensics.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)


@app.on_event("startup")
def startup_event():
    try:
        Base.metadata.create_all(bind=engine)
    except Exception:
        pass
    
    # Auto-seed demo case and initial evidence if database is freshly created
    try:
        from backend.app.core.database import SessionLocal
        from backend.app.models.case import Case
        from backend.app.services.evidence_service import EvidenceService
        from datasets.synthetic import generate_synthetic_dataset

        db = SessionLocal()
        try:
            if db.query(Case).count() == 0:
                demo_case = Case(
                    case_id="case_operation_shadowchain",
                    title="Operation ShadowChain — Illicit Layering & Mixer Investigation",
                    description="Forensic investigation into peeling chains, high-velocity mixer pooling, and rapid asset drains.",
                    investigator="Special Agent Vance",
                    status="ACTIVE",
                    priority="CRITICAL",
                    tags=["RANSOMWARE", "PEELING_CHAIN", "MIXER", "TRIAGE_PRIORITY_1"]
                )
                db.add(demo_case)
                db.commit()

                sample_txs = generate_synthetic_dataset(num_transactions=5, seed=42)
                for tx in sample_txs:
                    EvidenceService.ingest_transaction_evidence(
                        db=db,
                        case_id=demo_case.case_id,
                        transaction_id=tx["transaction_id"],
                        source_wallet=tx["source_wallet"],
                        destination_wallet=tx["destination_wallet"],
                        amount=float(tx["amount"]),
                        timestamp=float(tx["timestamp"]),
                        source="LIVE_INGESTION_STREAM",
                        source_identifier="MAINNET_NODE_01",
                        actor="Agent Vance",
                        role="INVESTIGATOR"
                    )
        finally:
            db.close()
    except Exception as e:
        print(f"[*] Startup auto-seeding note: {e}")


# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


from fastapi.responses import JSONResponse, Response

# Request timing & security header middleware
@app.middleware("http")
async def add_process_time_and_security_headers(request: Request, call_next):
    start_time = time.time()
    try:
        response = await call_next(request)
    except Exception as exc:
        import traceback
        print(f"[!] Unhandled Request Exception: {traceback.format_exc()}")
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal Server Error",
                "detail": str(exc),
                "type": type(exc).__name__,
                "path": request.url.path
            }
        )
    process_time = time.time() - start_time
    response.headers["X-Process-Time-Sec"] = f"{process_time:.4f}"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response


# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    import traceback
    print(f"[!] Global Exception Handler: {traceback.format_exc()}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "detail": str(exc),
            "type": type(exc).__name__,
            "path": request.url.path
        }
    )


# Include API Routers
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(cases.router, prefix=settings.API_V1_STR)
app.include_router(evidence.router, prefix=settings.API_V1_STR)
app.include_router(transactions.router, prefix=settings.API_V1_STR)
app.include_router(analyst_review.router, prefix=settings.API_V1_STR)
app.include_router(reports.router, prefix=settings.API_V1_STR)
app.include_router(models.router, prefix=settings.API_V1_STR)
app.include_router(experiments.router, prefix=settings.API_V1_STR)
app.include_router(dashboard.router, prefix=settings.API_V1_STR)
app.include_router(graph.router, prefix=settings.API_V1_STR)
app.include_router(blockchain.router, prefix=settings.API_V1_STR)
app.include_router(audit.router, prefix=settings.API_V1_STR)


@app.get("/favicon.ico")
def favicon():
    return Response(status_code=204)


@app.get("/")
def root():
    return {
        "platform": "TCF-FX — Trustworthy Cryptocurrency Forensic Intelligence Platform",
        "status": "ONLINE",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "api_v1": "/api/v1",
        "axiom": "AI Output != Forensic Finding != Legal Conclusion"
    }


@app.get("/health")
def health_check():
    return {
        "status": "HEALTHY",
        "service": "TCF-FX Forensic Backend",
        "version": "1.0.0",
        "trust_dimensions": [
            "Evidence Trust",
            "Analytical Trust",
            "Explanatory Trust",
            "Governance Trust",
            "Legal Trust"
        ]
    }
