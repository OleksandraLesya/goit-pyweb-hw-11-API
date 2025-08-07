# app/schemas/contacts.py

from datetime import date
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


# Base model for a contact. It contains common fields.
class ContactBase(BaseModel):
    first_name: str = Field(min_length=2, max_length=50)
    last_name: str = Field(min_length=2, max_length=50)
    email: EmailStr
    phone_number: str
    birthday: date
    notes: Optional[str] = None # Corrected from additional_data to notes


# Schema for creating a new contact. It inherits from the base model.
class ContactCreate(ContactBase):
    pass


# Schema for updating an existing contact. All fields are optional.
class ContactUpdate(BaseModel): # Changed to inherit directly from BaseModel for optional fields
    first_name: Optional[str] = Field(None, min_length=2, max_length=50)
    last_name: Optional[str] = Field(None, min_length=2, max_length=50)
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    birthday: Optional[date] = None
    notes: Optional[str] = None


# Schema for the API response. It includes the ID and other fields.
class ContactResponse(ContactBase):
    id: int
    user_id: int # NEW: Add user_id to the response model

    class Config:
        # This parameter allows Pydantic to work with SQLAlchemy ORM models
        from_attributes = True
