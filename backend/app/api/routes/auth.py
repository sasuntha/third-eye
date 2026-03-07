from fastapi import APIRouter, Depends, HTTPException, status
from supabase import Client
from app.db.supabase import get_supabase_client
from pydantic import BaseModel
from typing import Optional
from passlib.context import CryptContext
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/auth", tags=["auth"])

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    status: str
    message: str
    user: Optional[dict] = None
    role: Optional[str] = None


class SignupRequest(BaseModel):
    email: str
    password: str
    full_name: Optional[str] = None


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password"""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        logger.error(f"Password verification error: {str(e)}")
        return False


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest, client: Client = Depends(get_supabase_client)):
    """
    Login user with email and password from employees table.
    
    Returns:
    - role='chief': User is a chief, redirect to chief dashboard
    - role='employee' or role=null: User is an employee, redirect to employee dashboard
    """
    try:
        # Query employees table for matching email
        response = client.table("employees").select("*").eq("email", request.email).execute()
        
        if not response.data or len(response.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        employee = response.data[0]
        
        # Verify password - handle both hashed and plain text passwords
        password_hash = employee.get("password")
        if not password_hash:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Check if password is hashed (bcrypt hashes start with $2b$)
        if password_hash.startswith("$2b$") or password_hash.startswith("$2a$"):
            is_valid = verify_password(request.password, password_hash)
        else:
            # Fallback to plain text comparison (for development/testing)
            is_valid = request.password == password_hash
        
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Extract role (can be 'chief', 'employee', or null)
        role = employee.get("role")
        
        # Prepare user response (excluding password)
        user_data = {
            "id": employee.get("id"),
            "email": employee.get("email"),
            "full_name": employee.get("full_name"),
            "employee_id": employee.get("employee_id"),
            "role": role
        }
        
        logger.info(f"User {request.email} logged in successfully with role: {role}")
        
        return LoginResponse(
            status="success",
            message="Login successful",
            user=user_data,
            role=role or "employee"  # Default to employee if role is null
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )


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
