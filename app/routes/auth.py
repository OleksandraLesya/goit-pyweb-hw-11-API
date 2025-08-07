# app/routes/auth.py
from typing import Optional
import hashlib
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Security
from fastapi.security import OAuth2PasswordRequestForm, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.db import get_db
from app.repository import users as repository_users
from app.schemas.users import UserModel, UserResponse, TokenModel
from ..models.users import User
from app.services.auth import auth_service, oauth2_scheme

# We've determined that the `settings` object is not directly used in this file.
# Removing the import and initialization avoids a circular import dependency.


router = APIRouter(prefix="/auth", tags=["auth"])
get_refresh_token = HTTPBearer()


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(body: UserModel, db: AsyncSession = Depends(get_db)):
    """
    Registers a new user.

    Args:
        body: The UserModel containing user registration data.
        db: The asynchronous database session dependency.

    Returns:
        A UserResponse object with the newly created user's details.

    Raises:
        HTTPException: If an account with the provided email already exists.
    """
    user = await repository_users.get_user_by_email(body.email, db)
    if user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account already exists")

    body.password = auth_service.get_password_hash(body.password)
    new_user = await repository_users.create_user(body, db)
    return {"user": new_user, "detail": "User successfully created"}


@router.post("/login", response_model=TokenModel)
async def login(body: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    """
    Authenticates a user and provides access and refresh tokens.

    Args:
        body: The OAuth2PasswordRequestForm with the user's username and password.
        db: The asynchronous database session dependency.

    Returns:
        A TokenModel object containing the access and refresh tokens.

    Raises:
        HTTPException: If the user credentials are not valid.
    """
    user = await repository_users.get_user_by_email(body.username, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access_token = await auth_service.create_access_token(data={"sub": user.email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": user.email})

    await repository_users.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get("/refresh_token", response_model=TokenModel)
async def refresh_token(credentials: HTTPBearer = Security(get_refresh_token), db: AsyncSession = Depends(get_db)):
    """
    Refreshes access and refresh tokens using a valid refresh token.

    Args:
        credentials: The HTTPBearer token from the request header.
        db: The asynchronous database session dependency.

    Returns:
        A new TokenModel object with updated access and refresh tokens.

    Raises:
        HTTPException: If the refresh token is invalid or has been used.
    """
    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)

    user = await repository_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    if not user.refresh_token == token:
        await repository_users.update_token(user, None, db)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    access_token = await auth_service.create_access_token(data={"sub": user.email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": user.email})

    await repository_users.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(auth_service.get_current_user)):
    """
    Gets the current authenticated user's information.

    Args:
        current_user: The authenticated User object from the dependency.

    Returns:
        A UserResponse object with the current user's profile details.
    """
    return {"user": current_user, "detail": "User profile retrieved successfully"}
