# app/routes/contacts.py

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

# We import our database session and repository logic.
from app.database.db import get_db
from app.repository import contacts as repository_contacts
from app.schemas.contacts import ContactCreate, ContactUpdate, ContactResponse

# APIRouter helps to separate our routes into different files.
router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(
    body: ContactCreate, db: AsyncSession = Depends(get_db)
):
    """
    Create a new contact.
    """
    contact = await repository_contacts.create_contact(db, body)
    return contact


@router.get("/", response_model=List[ContactResponse])
async def get_all_contacts(
    skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)
):
    """
    Get a list of all contacts with pagination.
    """
    contacts = await repository_contacts.get_contacts(db, skip=skip, limit=limit)
    return contacts


@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact(contact_id: int, db: AsyncSession = Depends(get_db)):
    """
    Get a single contact by its ID.
    """
    contact = await repository_contacts.get_contact_by_id(db, contact_id)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    contact_id: int, body: ContactUpdate, db: AsyncSession = Depends(get_db)
):
    """
    Update an existing contact by its ID.
    """
    contact = await repository_contacts.update_contact(db, contact_id, body)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(contact_id: int, db: AsyncSession = Depends(get_db)):
    """
    Delete a contact by its ID.
    """
    contact = await repository_contacts.delete_contact(db, contact_id)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return None # We return None for a 204 No Content response


@router.get("/search/", response_model=List[ContactResponse])
async def search_contacts(query: str, db: AsyncSession = Depends(get_db)):
    """
    Search for contacts by first name, last name, or email.
    """
    return await repository_contacts.search_contacts(db, query)


@router.get("/birthdays/", response_model=List[ContactResponse])
async def upcoming_birthdays(db: AsyncSession = Depends(get_db)):
    """
    Get a list of contacts with upcoming birthdays in the next 7 days.
    """
    return await repository_contacts.upcoming_birthdays(db)
