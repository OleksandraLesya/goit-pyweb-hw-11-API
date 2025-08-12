# app/conf/config.py

from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    """
    Settings class to load environment variables from the .env file.
    This class reads the variables and makes them available to the application.
    """
    # Database settings
    DATABASE_URL: str

    # JWT authentication settings
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int

    # Email settings
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_PORT: int
    MAIL_SERVER: str

    # Redis settings for rate limiting
    REDIS_HOST: str
    REDIS_PORT: int

    # Cloudinary settings for avatar uploads
    CLOUDINARY_NAME: str
    CLOUDINARY_API_KEY: str
    CLOUDINARY_API_SECRET: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

@lru_cache()
def get_settings():
    """
    This function uses a cache to ensure the settings object is created
    only once, making it safe to call from multiple places without
    re-reading the .env file.
    """
    return Settings()

# Instead of creating a global settings object directly, we now use the function.
# This prevents potential import-related issues.
# The `settings` object will now be created only when `get_settings()` is called.
