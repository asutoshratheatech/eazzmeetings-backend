"""
Controller for authentication operations (Register, Login).
"""
from datetime import timedelta
from fastapi import HTTPException, status
from app.models.database.users_collection import UserCollection, UserSecretsCollection
from app.schemas.users_schema import UserCreate, UserLogin, Token
from app.security import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
    verify_password,
)
from app.env_settings import env

async def register_ctrl(user_in: UserCreate) -> Token:
    """
    Handles user registration:
    1. Checks if email/username exists.
    2. Creates User record.
    3. Hashes password and creates UserSecrets.
    4. Generates and returns JWT tokens.
    """
    # Check if user exists
    existing_user_email = await UserCollection.find_one(UserCollection.email == user_in.email)
    if existing_user_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )

    existing_user_username = await UserCollection.find_one(
        UserCollection.username == user_in.username
    )
    if existing_user_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this username already exists",
        )

    # Create User
    user = UserCollection(
        username=user_in.username,
        email=user_in.email,
        full_name=user_in.full_name,
        phone=user_in.phone,
        org_id=None
    )
    await user.create()

    # Create Secrets
    hashed_password = get_password_hash(user_in.password)
    user_secrets = UserSecretsCollection(
        user_id=user.id,
        password_hash=hashed_password,
        org_id=user.org_id
    )
    await user_secrets.create()

    # Create Tokens
    token_data = {
        "sub": str(user.id),
        "user_name": user.username,
        "user_email": user.email,
        "role_name": "user",
        "org_id": str(user.org_id) if user.org_id else None
    }

    access_token_expires = timedelta(minutes=int(env.ACCESS_TOKEN_EXPIRE_MINUTES or 15))
    access_token = create_access_token(
        data=token_data, expires_delta=access_token_expires
    )

    refresh_token_expires = timedelta(minutes=int(env.REFRESH_TOKEN_EXPIRE_MINUTES or 10080))
    refresh_token = create_refresh_token(
        data=token_data, expires_delta=refresh_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": refresh_token
    }

async def login_ctrl(user_in: UserLogin) -> Token:
    """
    Handles user login:
    1. Finds user by email or username.
    2. Verifies password.
    3. Generates and returns JWT tokens.
    """
    # Find user by email (primary) or username
    user = await UserCollection.find_one(UserCollection.email == user_in.email)
    if not user:
        # Fallback to username check
        user = await UserCollection.find_one(UserCollection.username == user_in.email)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify password
    user_secrets = await UserSecretsCollection.find_one(
        UserSecretsCollection.user_id == user.id
    )
    if not user_secrets or not verify_password(user_in.password, user_secrets.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create Tokens
    token_data = {
        "sub": str(user.id),
        "user_name": user.username,
        "user_email": user.email,
        "role_name": "user",
        "org_id": str(user.org_id) if user.org_id else None
    }

    access_token_expires = timedelta(minutes=int(env.ACCESS_TOKEN_EXPIRE_MINUTES or 15))
    access_token = create_access_token(
        data=token_data, expires_delta=access_token_expires
    )

    refresh_token_expires = timedelta(minutes=int(env.REFRESH_TOKEN_EXPIRE_MINUTES or 10080))
    refresh_token = create_refresh_token(
        data=token_data, expires_delta=refresh_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": refresh_token
    }

