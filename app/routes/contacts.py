from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.db import get_db
from app.repository import contacts as repository_contacts
from app.schemas.contacts import ContactCreate, ContactUpdate, ContactResponse
from app.services.auth import auth_service
from app.models.users import User

# Create an API router for contact-related endpoints.
router = APIRouter(prefix="/contacts", tags=["contacts"])


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


@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
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
