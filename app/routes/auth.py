# app/routes/auth.py

import json
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Security, BackgroundTasks, Request
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

from app.database.db import get_db
from app.repository import users as repository_users
from app.schemas.users import UserModel, UserResponse, TokenModel, RequestEmail, PasswordResetModel
from app.models.users import User
from app.services.auth import auth_service
from app.services.email import send_email as send_email_service
from app.services.email import send_password_reset_email as send_password_reset_email_service
from app.dependencies import redis_client_var

router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBearer()


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(
        body: UserModel,
        background_tasks: BackgroundTasks,
        request: Request,
        db: AsyncSession = Depends(get_db)
):
    """
    Registers a new user and sends a verification email.
    """
    user = await repository_users.get_user_by_email(body.email, db)
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Account with this email already exists"
        )

    body.password = auth_service.get_password_hash(body.password)
    new_user = await repository_users.create_user(body, db)

    background_tasks.add_task(send_email_service, new_user.email, new_user.username, str(request.base_url))

    return UserResponse(user=new_user, detail="User successfully created")


@router.post("/login", response_model=TokenModel)
async def login(
        body: OAuth2PasswordRequestForm = Depends(),
        db: AsyncSession = Depends(get_db)
):
    """
    Authenticates a user and provides access and refresh tokens.
    """
    user = await repository_users.get_user_by_email(body.username, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    # Змінюємо 'user.confirmed' на 'user.email_verified'
    if not user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email not confirmed"
        )

    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    access_token = auth_service.create_access_token(data={"sub": user.email})
    refresh_token = auth_service.create_refresh_token(data={"sub": user.email})
    await repository_users.update_token(user, refresh_token, db)

    # Get the Redis client from the ContextVar
    redis_client = redis_client_var.get()

    # Store the user data in Redis as a JSON string
    user_data_to_cache = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "avatar": user.avatar
    }
    await redis_client.set(f"user:{user.email}", json.dumps(user_data_to_cache), ex=3600)

    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get("/refresh_token", response_model=TokenModel)
async def refresh_token(
        credentials: HTTPAuthorizationCredentials = Security(security),
        db: AsyncSession = Depends(get_db)
):
    """
    Refreshes the access token using a valid refresh token.
    """
    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    if user.refresh_token != token:
        await repository_users.update_token(user, None, db)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    access_token = auth_service.create_access_token(data={"sub": user.email})
    refresh_token = auth_service.create_refresh_token(data={"sub": user.email})
    await repository_users.update_token(user, refresh_token, db)

    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(auth_service.get_current_user)):
    """
    Gets the current authenticated user's information.
    """
    return UserResponse(user=current_user, detail="User profile retrieved successfully")


@router.get("/confirmed_email/{token}")
async def confirmed_email(token: str, db: AsyncSession = Depends(get_db)):
    """
    Confirms a user's email using a token from a verification link.
    """
    email = auth_service.get_email_from_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification error"
        )
    # Змінюємо 'user.confirmed' на 'user.email_verified'
    if user.email_verified:
        return {"message": "Your email is already confirmed"}
    await repository_users.confirmed_email(email, db)
    return {"message": "Email confirmed"}


@router.post("/request_reset_password", status_code=status.HTTP_200_OK)
async def request_password_reset(
        body: RequestEmail,
        background_tasks: BackgroundTasks,
        request: Request,
        db: AsyncSession = Depends(get_db)
):
    """
    Requests a password reset token to be sent to the user's email.
    """
    user = await repository_users.get_user_by_email(body.email, db)
    if user:
        token_reset = auth_service.create_reset_token({"sub": user.email})
        background_tasks.add_task(send_password_reset_email_service, user.email, user.username, str(request.base_url), token_reset)
        return {"message": "If a user with this email exists, a password reset token has been sent."}

    # Don't give away whether the user exists or not for security reasons.
    return {"message": "If a user with this email exists, a password reset token has been sent."}


@router.post("/reset_password", status_code=status.HTTP_200_OK)
async def reset_password(
        body: PasswordResetModel,
        db: AsyncSession = Depends(get_db)
):
    """
    Resets the user's password using a valid reset token.
    """
    email = await auth_service.get_email_from_reset_token(body.token)
    user = await repository_users.get_user_by_email(email, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token"
        )

    # Hash the new password before updating
    hashed_password = auth_service.get_password_hash(body.new_password)
    await repository_users.update_password(user, hashed_password, db)

    return {"message": "Password has been successfully reset."}
