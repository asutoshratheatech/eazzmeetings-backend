"""
Security module for application, handling password hashing and JWT tokens.
"""
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.env_settings import env
from app.schemas.common_schema import UserJWT

# Password Hashing Context
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# OAuth2 Scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain password against a hashed password.
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Generates a hash for a plain password using Argon2.
    """
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Creates a JWT access token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=int(env.ACCESS_TOKEN_EXPIRE_MINUTES or 15)
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, env.SECRET_KEY, algorithm=env.ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Creates a JWT refresh token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=int(env.REFRESH_TOKEN_EXPIRE_MINUTES or 10080)
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, env.SECRET_KEY, algorithm=env.ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decodes the JWT token and returns the payload.
    Use validate_jwt_token for stricter validation with exceptions.
    """
    try:
        payload = jwt.decode(token, env.SECRET_KEY, algorithms=[env.ALGORITHM])
        return payload
    except JWTError:
        return None


def validate_jwt_token(token: str) -> dict:
    """
    Validates a JWT token and returns the payload.
    Raises ValueError with specific messages for invalid or expired tokens.
    """
    try:
        payload = jwt.decode(token, env.SECRET_KEY, algorithms=[env.ALGORITHM])
        if payload is None:
            raise ValueError("Invalid token payload")
        return payload
    except JWTError as e:
        raise ValueError(f"Invalid token: {str(e)}") from e


async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserJWT:
    """
    Dependency to get the current user from the JWT token.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_token(token)
    if payload is None:
        raise credentials_exception

    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    # Improving performance by returning payload directly as UserJWT without DB call if not needed,
    # or add DB call if strict verification is required.
    # Based on UserJWT definition "sub is UserCollection._id", we have what we need.
    return payload  # type: ignore
