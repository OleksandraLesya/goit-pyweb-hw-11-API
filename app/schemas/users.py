# app/schemas/users.py

from datetime import datetime
from pydantic import BaseModel, Field, EmailStr


class UserModel(BaseModel):
    """
    Pydantic model for user registration data.
    """
    email: EmailStr
    password: str = Field(min_length=6, max_length=10)


class UserDb(BaseModel):
    """
    Pydantic model for user data as stored in the database.
    """
    id: int
    email: EmailStr
    created_at: datetime
    avatar: str | None # Avatar can be optional

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    """
    Pydantic model for the user registration response.
    """
    user: UserDb
    detail: str = "User successfully created"


class TokenModel(BaseModel):
    """
    Pydantic model for JWT tokens (access and refresh).
    """
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
