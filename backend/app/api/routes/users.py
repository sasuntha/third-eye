from fastapi import APIRouter, Depends
from supabase import Client
from app.db.supabase import get_supabase_client
from pydantic import BaseModel
from typing import Optional, List


router = APIRouter(prefix="/api/users", tags=["users"])


class UserProfile(BaseModel):
    id: Optional[str] = None
    email: str
    full_name: Optional[str] = None
    department: Optional[str] = None
    role: Optional[str] = None


@router.get("/me")
async def get_current_user(client: Client = Depends(get_supabase_client)):
    """Get current logged-in user"""
    try:
        user = client.auth.get_user()
        return {"status": "success", "user": user}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.get("/")
async def get_users(client: Client = Depends(get_supabase_client)):
    """Get all users"""
    try:
        response = client.table("users").select("*").execute()
        return {"status": "success", "users": response.data}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.post("/")
async def create_user(user: UserProfile, client: Client = Depends(get_supabase_client)):
    """Create new user profile"""
    try:
        response = client.table("users").insert(user.model_dump()).execute()
        return {"status": "success", "user": response.data}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.get("/{user_id}")
async def get_user(user_id: str, client: Client = Depends(get_supabase_client)):
    """Get user by ID"""
    try:
        response = client.table("users").select("*").eq("id", user_id).execute()
        return {"status": "success", "user": response.data}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.put("/{user_id}")
async def update_user(user_id: str, user: UserProfile, client: Client = Depends(get_supabase_client)):
    """Update user profile"""
    try:
        response = client.table("users").update(user.model_dump()).eq("id", user_id).execute()
        return {"status": "success", "user": response.data}
    except Exception as e:
        return {"status": "error", "message": str(e)}
