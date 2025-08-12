# app/services/auth.py

import json
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

from sqlalchemy.ext.asyncio import AsyncSession
from app.database.db import get_db
from app.repository import users as repository_users
from app.models.users import User
from app.conf.config import get_settings
from app.dependencies import redis_client_var

settings = get_settings()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM


class Auth:
    """
    Authentication service class.

    Handles password hashing, JWT token creation, and token verification.
    """

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verifies a plain password against a hashed password.

        :param plain_password: The password provided by the user.
        :param hashed_password: The stored hashed password.
        :return: True if passwords match, False otherwise.
        """
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """
        Hashes a plain password.

        :param password: The plain password to hash.
        :return: The hashed password string.
        """
        return pwd_context.hash(password)

    def create_access_token(self, data: dict, expires_delta: Optional[float] = None) -> str:
        """
        Creates a new JWT access token.

        :param data: Dictionary containing the payload for the token (e.g., user email).
        :param expires_delta: Optional timedelta for token expiration.
        :return: The encoded JWT access token.
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + timedelta(seconds=expires_delta)
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=15)
        to_encode.update({"iat": datetime.now(timezone.utc), "exp": expire, "scope": "access_token"})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    def create_refresh_token(self, data: dict, expires_delta: Optional[float] = None) -> str:
        """
        Creates a new JWT refresh token.

        :param data: Dictionary containing the payload for the token (e.g., user email).
        :param expires_delta: Optional timedelta for token expiration.
        :return: The encoded JWT refresh token.
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + timedelta(seconds=expires_delta)
        else:
            expire = datetime.now(timezone.utc) + timedelta(days=7)
        to_encode.update({"iat": datetime.now(timezone.utc), "exp": expire, "scope": "refresh_token"})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    def create_email_token(self, data: dict, expires_delta: Optional[float] = None):
        """
        Creates a JWT token for email verification with an expiration time.

        :param data: The data to be encoded into the token.
        :type data: dict
        :param expires_delta: The expiration time in seconds. Defaults to 900 (15 minutes).
        :type expires_delta: Optional[float]
        :return: The encoded JWT token.
        :rtype: str
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "email_verification"})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    async def decode_refresh_token(self, refresh_token: str) -> str:
        """
        Decodes a JWT refresh token and returns the email.

        :param refresh_token: The refresh token string.
        :raises HTTPException: If the token is invalid or expired.
        :return: The email extracted from the token.
        """
        try:
            payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
            if payload['scope'] == 'refresh_token':
                email = payload['sub']
                return email
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid scope for token')
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate credentials')

    def get_email_from_token(self, token: str) -> str:
        """
        Decodes a JWT email verification token and returns the email.

        :param token: The verification token string.
        :raises HTTPException: If the token is invalid or expired.
        :return: The email extracted from the token.
        """
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            if payload['scope'] == 'email_verification':
                email = payload['sub']
                return email
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid scope for token')
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate credentials')

    def create_reset_token(self, data: dict, expires_delta: Optional[float] = None):
        """
        Creates a JWT token for password reset with an expiration time.

        :param data: The data to be encoded into the token.
        :type data: dict
        :param expires_delta: The expiration time in seconds. Defaults to 900 (15 minutes).
        :type expires_delta: Optional[float]
        :return: The encoded JWT token.
        :rtype: str
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "password_reset"})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    def get_email_from_reset_token(self, token: str) -> str:
        """
        Decodes a JWT password reset token and returns the email.

        :param token: The reset token string.
        :raises HTTPException: If the token is invalid or expired.
        :return: The email extracted from the token.
        """
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            if payload['scope'] == 'password_reset':
                email = payload['sub']
                return email
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid scope for token')
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate credentials')

    async def get_current_user(self, token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> User:
        """
        Retrieves the current authenticated user from Redis cache or the database.

        :param token: The JWT access token from the request header.
        :param db: The asynchronous database session.
        :raises HTTPException: If the token is invalid, expired, or user not found.
        :return: The authenticated User object.
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            if payload['scope'] == 'access_token':
                email = payload['sub']
            else:
                raise credentials_exception
        except JWTError:
            raise credentials_exception

        # Get the Redis client from the ContextVar
        redis_client = redis_client_var.get()

        # Try to get the user from Redis cache first
        user_data_json = await redis_client.get(f"user:{email}")

        if user_data_json:
            user_data = json.loads(user_data_json)
            # We create a User object from the cached dictionary
            user = User(**user_data)
            return user

        # If the user is not in the cache, retrieve from the database
        user = await repository_users.get_user_by_email(email, db)
        if user is None:
            raise credentials_exception

        # And then save the user to the cache for future requests
        user_data_to_cache = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "avatar": user.avatar
        }
        await redis_client.set(f"user:{user.email}", json.dumps(user_data_to_cache), ex=3600)

        return user


auth_service = Auth()
