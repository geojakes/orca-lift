"""Authentication API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from ...db.repositories import UserRepository
from ...models.auth import User
from ..auth import create_token_pair, hash_password, verify_password
from ..deps import get_current_user

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


class RegisterRequest(BaseModel):
    email: str
    password: str
    name: str = ""


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 3600


@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(req: RegisterRequest):
    """Register a new user."""
    repo = UserRepository()
    existing = await repo.get_by_email(req.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )
    
    user = User(
        email=req.email,
        hashed_password=hash_password(req.password),
        name=req.name,
    )
    user_id = await repo.create(user)
    return create_token_pair(user_id)


@router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest):
    """Log in and receive tokens."""
    repo = UserRepository()
    user = await repo.get_by_email(req.email)
    
    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    
    return create_token_pair(user.id)


class MeResponse(BaseModel):
    id: int
    email: str
    name: str


@router.get("/me", response_model=MeResponse)
async def get_me(user: User = Depends(get_current_user)):
    """Get current user info."""
    return MeResponse(id=user.id, email=user.email, name=user.name)
