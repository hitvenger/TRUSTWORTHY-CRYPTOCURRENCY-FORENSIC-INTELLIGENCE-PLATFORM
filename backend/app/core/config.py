"""
TCF-FX Backend Configuration Settings.
"""

import os
from pydantic_settings import BaseSettings
from typing import List


def _get_default_database_url() -> str:
    env_db = os.getenv("DATABASE_URL")
    if env_db:
        return env_db
    if os.getenv("VERCEL") or os.getenv("AWS_LAMBDA_FUNCTION_NAME") or os.getenv("LAMBDA_TASK_ROOT"):
        return "sqlite:////tmp/tcf_forensics.db"
    try:
        test_path = "./.write_test"
        with open(test_path, "w") as f:
            f.write("1")
        os.remove(test_path)
        return "sqlite:///./tcf_forensics.db"
    except Exception:
        return "sqlite:////tmp/tcf_forensics.db"


class Settings(BaseSettings):
    PROJECT_NAME: str = "TCF-FX Forensic Intelligence Platform"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "tcf_fx_super_secret_forensic_key_2026_salt_9981")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # Database: Auto-detects /tmp for serverless (Vercel) or local SQLite/PostgreSQL
    DATABASE_URL: str = _get_default_database_url()
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "*"
    ]

    # Blockchain
    ETH_RPC_URL: str = os.getenv("ETH_RPC_URL", "")
    CONTRACT_ADDRESS: str = os.getenv("CONTRACT_ADDRESS", "")

    class Config:
        case_sensitive = True


settings = Settings()
