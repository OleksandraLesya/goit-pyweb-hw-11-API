# app/conf/config.py

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """
    Settings class to load environment variables from the .env file.
    This class reads the variables and makes them available to the application.
    """
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str

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
