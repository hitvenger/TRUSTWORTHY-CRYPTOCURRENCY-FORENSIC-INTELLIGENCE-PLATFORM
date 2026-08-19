"""
TCF-FX Backend Configuration Settings.
"""

import os
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    PROJECT_NAME: str = "TCF-FX Forensic Intelligence Platform"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "tcf_fx_super_secret_forensic_key_2026_salt_9981")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # Database: SQLite default for seamless local running, PostgreSQL for production
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./tcf_forensics.db")
    
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
