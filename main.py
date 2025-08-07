# main.py

from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.db import get_db
from app.routes import contacts as contacts_router # Renamed for clarity
from app.routes import auth as auth_router # NEW: Import the auth router


app = FastAPI()

# Include the contacts' router. All contact endpoints will be prefixed with /api.
app.include_router(contacts_router.router, prefix="/api")
# NEW: Include the authentication router. All auth endpoints will be prefixed with /api.
app.include_router(auth_router.router, prefix="/api")


@app.get("/")
async def read_root():
    """
    Root endpoint of the API.
    """
    return {"message": "Welcome to the Contacts API!"}
