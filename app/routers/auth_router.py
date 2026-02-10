"""
Authentication router for handling user registration and login.
"""
from fastapi import APIRouter
from app.schemas.users_schema import UserCreate, UserLogin, AuthResponse
from app.controllers import register_ctrl, login_ctrl

router = APIRouter(tags=["Authentication"])

@router.post("/register", response_model=AuthResponse)
async def register(user_in: UserCreate):
    """
    Register a new user and return an access token.
    """
    return await register_ctrl(user_in)

@router.post("/login", response_model=AuthResponse)
async def login(user_in: UserLogin):
    """
    Login an existing user and return an access token.
    """
    return await login_ctrl(user_in)
