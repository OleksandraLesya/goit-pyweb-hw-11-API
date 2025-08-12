# app/dependencies.py

import redis.asyncio as redis
from contextvars import ContextVar

# Define the Redis client as a ContextVar to be used across different modules
redis_client_var: ContextVar[redis.Redis] = ContextVar("redis_client_var")
