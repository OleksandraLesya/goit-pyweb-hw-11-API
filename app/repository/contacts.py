# app/repository/contacts.py

from typing import List, Type
from sqlalchemy import select, update, delete, and_
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta, date
import calendar

from app.models.contacts import Contact
from app.models.users import User  # NEW: Import User model
from app.schemas.contacts import ContactCreate, ContactUpdate


# This is our repository. It will contain all the logic for interacting with the database.


async def get_contacts(db: AsyncSession, user: User, skip: int = 0, limit: int = 100) -> List[Contact]:
    """
    Get a list of all contacts for a specific user from the database with pagination.
    """
    # Filter contacts by user_id
    query = select(Contact).filter(Contact.user_id == user.id).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


async def get_contact_by_id(db: AsyncSession, contact_id: int, user: User) -> Contact | None:
    """
    Get a single contact by its ID for a specific user.
    """
    # Filter contact by ID and user_id
    query = select(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == user.id))
    result = await db.execute(query)
    return result.scalars().one_or_none()


async def create_contact(db: AsyncSession, body: ContactCreate, user: User) -> Contact:
    """
    Create a new contact in the database for a specific user.
    """
    # Assign contact to the current user
    new_contact = Contact(**body.model_dump(), user_id=user.id)
    db.add(new_contact)
    await db.commit()
    await db.refresh(new_contact)
    return new_contact


async def update_contact(db: AsyncSession, contact_id: int, body: ContactUpdate, user: User) -> Contact | None:
    """
    Update an existing contact by its ID for a specific user.
    """
    # Ensure contact belongs to the current user
    contact = await get_contact_by_id(db, contact_id, user)

    if contact:
        for field, value in body.model_dump(exclude_unset=True).items():
            setattr(contact, field, value)
        await db.commit()
        await db.refresh(contact)
    return contact


async def delete_contact(db: AsyncSession, contact_id: int, user: User) -> Contact | None:
    """
    Delete a contact by its ID for a specific user.
    """
    # Ensure contact belongs to the current user
    contact = await get_contact_by_id(db, contact_id, user)
    if contact:
        await db.delete(contact)
        await db.commit()
    return contact


async def search_contacts(db: AsyncSession, query: str, user: User) -> List[Contact]:
    """
    Search for contacts by first name, last name, or email for a specific user.
    """
    # Filter search results by user_id
    result = await db.execute(
        select(Contact).filter(
            (Contact.user_id == user.id) &
            (
                (Contact.first_name.ilike(f"%{query}%")) |
                (Contact.last_name.ilike(f"%{query}%")) |
                (Contact.email.ilike(f"%{query}%"))
            )
        )
    )
    return result.scalars().all()


async def upcoming_birthdays(db: AsyncSession, user: User) -> List[Contact]:
    """
    Get a list of contacts with upcoming birthdays in the next 7 days for a specific user.
    """
    today = date.today()
    in_seven_days = today + timedelta(days=7)

    # We fetch all contacts for the user and then filter for upcoming birthdays in Python.
    # This approach is easier to handle leap year logic correctly than a complex SQL query.
    contacts = await get_contacts(db, user)

    upcoming = []
    for contact in contacts:
        # Check for Feb 29th and a non-leap year BEFORE calling replace()
        if contact.birthday.month == 2 and contact.birthday.day == 29 and not calendar.isleap(today.year):
            # If it's Feb 29th and the current year is not a leap year, we treat it as Feb 28th
            bday_this_year = contact.birthday.replace(day=28, year=today.year)
        else:
            # For all other cases, just replace the year
            bday_this_year = contact.birthday.replace(year=today.year)

        if today <= bday_this_year <= in_seven_days:
            upcoming.append(contact)

    return upcoming
