# app/routes/contacts.py

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Path, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
import time
import redis.asyncio as redis  # Import redis for type hints and to be explicit

# Import redis_client_var from the new dependencies file
from app.dependencies import redis_client_var

from app.database.db import get_db
from app.repository import contacts as repository_contacts
from app.schemas.contacts import ContactCreate, ContactUpdate, ContactResponse
from app.services.auth import auth_service
from app.models.users import User

# Create an API router for contact-related endpoints.
router = APIRouter(prefix="/contacts", tags=["contacts"])


# --- Rate Limiting Dependency ---
async def rate_limit(request: Request):
    """
    Manually implements rate limiting using Redis.
    Allows only 5 requests per minute per user.
    """
    # Get the Redis client from the ContextVar
    redis_client = redis_client_var.get()

    # Get the user's IP address as a unique identifier
    user_ip = request.client.host

    # Define the key for Redis: "rate_limit:<IP_ADDRESS>"
    key = f"rate_limit:{user_ip}"

    # Increment the counter for this key in Redis
    # 'incr' is atomic, so it's safe for concurrent requests
    current_requests = await redis_client.incr(key)

    # Set the expiration time for the key (60 seconds)
    # This is done only for the first request to ensure the counter resets
    if current_requests == 1:
        await redis_client.expire(key, 60)

    # Check if the number of requests exceeds the limit (5 requests per minute)
    if current_requests > 5:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests. Please try again later."
        )


# --- END of Rate Limiting Dependency ---


@router.get("/search/", response_model=List[ContactResponse])
async def search_contacts(
        query: str = Query(..., min_length=1),
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(auth_service.get_current_user)
):
    """
    Search for contacts by first name, last name, or email for the authenticated user.
    """
    contacts = await repository_contacts.search_contacts(db, query, current_user)
    if not contacts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contacts


@router.get("/birthdays/", response_model=List[ContactResponse])
async def upcoming_birthdays(
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(auth_service.get_current_user)
):
    """
    Get a list of contacts with upcoming birthdays in the next 7 days for the authenticated user.
    """
    contacts = await repository_contacts.upcoming_birthdays(db, current_user)
    return contacts


@router.get("/", response_model=List[ContactResponse])
async def get_contacts(
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=0),
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(auth_service.get_current_user)
):
    """
    Get a list of all contacts for the authenticated user with pagination.
    """
    contacts = await repository_contacts.get_contacts(db, current_user, skip, limit)
    return contacts


@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact_by_id(
        contact_id: int = Path(ge=1),
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(auth_service.get_current_user)
):
    """
    Get a single contact by its ID for the authenticated user.
    """
    contact = await repository_contacts.get_contact_by_id(db, contact_id, current_user)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact


@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(rate_limit)])
async def create_contact(
        body: ContactCreate,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(auth_service.get_current_user)
):
    """
    Create a new contact for the authenticated user.
    """
    contact = await repository_contacts.create_contact(db, body, current_user)
    return contact


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(
        body: ContactUpdate,
        contact_id: int = Path(ge=1),
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(auth_service.get_current_user)
):
    """
    Update an existing contact by its ID for the authenticated user.
    """
    contact = await repository_contacts.update_contact(db, contact_id, body, current_user)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact


@router.delete("/{contact_id}", response_model=ContactResponse)
async def delete_contact(
        contact_id: int = Path(ge=1),
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(auth_service.get_current_user)
):
    """
    Delete a contact by its ID for the authenticated user.
    """
    contact = await repository_contacts.delete_contact(db, contact_id, current_user)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact
