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
    additional_data: Optional[str] = None

# Schema for creating a new contact. It inherits from the base model.
class ContactCreate(ContactBase):
    pass

# Schema for updating an existing contact. All fields are optional.
class ContactUpdate(ContactBase):
    pass

# Schema for the API response. It includes the ID and other fields.
class ContactResponse(ContactBase):
    id: int

    class Config:
        # This parameter allows Pydantic to work with SQLAlchemy ORM models
        from_attributes = True
