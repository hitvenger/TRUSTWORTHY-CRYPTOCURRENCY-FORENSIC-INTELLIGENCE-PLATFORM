"""
Authentication & Role Management Endpoints for TCF-FX.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Dict, Any, Optional

from backend.app.core.security import create_access_token, get_current_user, get_password_hash, verify_password

router = APIRouter(prefix="/auth", tags=["Authentication"])


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]


# Seeded demo credentials
DEMO_USERS = {
    "admin": {"password_hash": get_password_hash("admin123"), "role": "ADMIN", "user_id": "usr_001"},
    "investigator": {"password_hash": get_password_hash("investigator123"), "role": "INVESTIGATOR", "user_id": "usr_002"},
    "analyst": {"password_hash": get_password_hash("analyst123"), "role": "ANALYST", "user_id": "usr_003"},
    "auditor": {"password_hash": get_password_hash("auditor123"), "role": "AUDITOR", "user_id": "usr_004"},
    "viewer": {"password_hash": get_password_hash("viewer123"), "role": "VIEWER", "user_id": "usr_005"},
}


@router.post("/login", response_model=LoginResponse)
def login(req: LoginRequest):
    user_record = DEMO_USERS.get(req.username.lower())
    if not user_record or not verify_password(req.password, user_record["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    role = user_record["role"]
    user_id = user_record["user_id"]
    token = create_access_token(data={"sub": req.username, "role": role, "user_id": user_id})
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user_id,
            "username": req.username,
            "role": role,
            "email": f"{req.username}@tcf-fx.internal"
        }
    }


@router.get("/me")
def get_current_user_profile(current_user: Dict[str, Any] = Depends(get_current_user)):
    return current_user
