from fastapi import APIRouter, Depends
from supabase import Client
from app.db.supabase import get_supabase_client
from pydantic import BaseModel
from typing import Optional


router = APIRouter(prefix="/api/auth", tags=["auth"])


class LoginRequest(BaseModel):
    email: str
    password: str


class SignupRequest(BaseModel):
    email: str
    password: str
    full_name: Optional[str] = None


@router.post("/login")
async def login(request: LoginRequest, client: Client = Depends(get_supabase_client)):
    """Login user with email and password"""
    try:
        response = client.auth.sign_in_with_password({
            "email": request.email,
            "password": request.password
        })
        return {"status": "success", "user": response.user, "session": response.session}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.post("/signup")
async def signup(request: SignupRequest, client: Client = Depends(get_supabase_client)):
    """Create new user account"""
    try:
        response = client.auth.sign_up({
            "email": request.email,
            "password": request.password
        })
        return {"status": "success", "user": response.user}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.post("/logout")
async def logout(client: Client = Depends(get_supabase_client)):
    """Logout user"""
    try:
        client.auth.sign_out()
        return {"status": "success", "message": "Logged out successfully"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
