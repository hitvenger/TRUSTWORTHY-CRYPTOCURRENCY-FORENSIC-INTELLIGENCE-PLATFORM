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
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="TCF-FX Forensic Intelligence Platform API",
    description="Evidence-aware AI for explainable cryptocurrency digital forensics.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request timing & security header middleware
@app.middleware("http")
async def add_process_time_and_security_headers(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time-Sec"] = f"{process_time:.4f}"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response


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
