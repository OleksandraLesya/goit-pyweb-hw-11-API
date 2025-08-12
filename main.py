# HWPW11/main.py

import os
import redis.asyncio as redis
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import contacts as contacts_router
from app.routes import auth as auth_router
from app.routes import users as users_router
from app.dependencies import redis_client_var

app = FastAPI()

# --- CORS Middleware ---
# Define allowed origins for CORS.
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Routers ---
app.include_router(auth_router.router, prefix="/api")
app.include_router(contacts_router.router, prefix="/api")
app.include_router(users_router.router, prefix="/api")


# --- Startup and Shutdown Events ---
@app.on_event("startup")
async def startup_event():
    """
    Initializes the Redis connection on application startup.
    """
    try:
        # We'll get Redis settings directly from environment variables.
        # This assumes REDIS_HOST and REDIS_PORT are set in your .env file.
        redis_host = os.environ.get("REDIS_HOST", "localhost")
        redis_port = int(os.environ.get("REDIS_PORT", 6379))

        r = await redis.Redis(
            host=redis_host,
            port=redis_port,
            db=0,
            encoding="utf-8",
            decode_responses=True
        )
        redis_client_var.set(r)
        print("Redis connection initialized and stored in ContextVar.")
    except Exception as e:
        print(f"Failed to initialize Redis connection: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Closes the Redis connection on application shutdown.
    """
    redis_client = redis_client_var.get()
    if redis_client:
        await redis_client.close()
        print("Redis connection closed.")


# --- Root Endpoint ---
@app.get("/")
async def read_root():
    """
    Root endpoint of the API.
    """
    return {"message": "Welcome to the Contacts API!"}
