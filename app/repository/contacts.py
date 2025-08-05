from typing import List, Type
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta, date
import calendar  # NEW: Import calendar module to check for leap years

from app.models.contacts import Contact
from app.schemas.contacts import ContactCreate, ContactUpdate


# This is our repository. It will contain all the logic for interacting with the database.


async def get_contacts(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Contact]:
    """
    Get a list of all contacts from the database with pagination.
    """
    query = select(Contact).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


async def get_contact_by_id(db: AsyncSession, contact_id: int) -> Contact | None:
    """
    Get a single contact by its ID.
    """
    query = select(Contact).filter(Contact.id == contact_id)
    result = await db.execute(query)
    return result.scalars().one_or_none()


async def create_contact(db: AsyncSession, body: ContactCreate) -> Contact:
    """
    Create a new contact in the database.
    """
    new_contact = Contact(**body.model_dump())
    db.add(new_contact)
    await db.commit()
    await db.refresh(new_contact)
    return new_contact


async def update_contact(db: AsyncSession, contact_id: int, body: ContactUpdate) -> Contact | None:
    """
    Update an existing contact by its ID.
    """
    contact = await get_contact_by_id(db, contact_id)

    if contact:
        # Use body.model_dump(exclude_unset=True) to only update provided fields
        # This is crucial after making ContactUpdate fields optional
        for field, value in body.model_dump(exclude_unset=True).items():
            setattr(contact, field, value)
        await db.commit()
        await db.refresh(contact)
    return contact


async def delete_contact(db: AsyncSession, contact_id: int) -> Contact | None:
    """
    Delete a contact by its ID.
    """
    contact = await get_contact_by_id(db, contact_id)
    if contact:
        await db.delete(contact)
        await db.commit()
    return contact


async def search_contacts(db: AsyncSession, query: str) -> List[Contact]:
    """
    Search for contacts by first name, last name, or email.
    """
    result = await db.execute(
        select(Contact).filter(
            (Contact.first_name.ilike(f"%{query}%")) |
            (Contact.last_name.ilike(f"%{query}%")) |
            (Contact.email.ilike(f"%{query}%"))
        )
    )
    return result.scalars().all()


async def upcoming_birthdays(db: AsyncSession) -> List[Contact]:
    """
    Get a list of contacts with upcoming birthdays in the next 7 days.
    FIX 3: Handles February 29th correctly in non-leap years.
    """
    today = date.today()
    next_week = today + timedelta(days=7)

    contacts = await get_contacts(db)

    upcoming = []
    for contact in contacts:
        # NEW FIX: Check for Feb 29th and non-leap year BEFORE calling replace()
        if contact.birthday.month == 2 and contact.birthday.day == 29 and not calendar.isleap(today.year):
            # If it's Feb 29th and current year is not a leap year, treat it as Feb 28th
            bday_this_year = contact.birthday.replace(day=28, year=today.year)
        else:
            # For all other cases, just replace the year
            bday_this_year = contact.birthday.replace(year=today.year)

        if today <= bday_this_year <= next_week:
            upcoming.append(contact)

    return upcoming
