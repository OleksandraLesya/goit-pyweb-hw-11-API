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
    notes: Optional[str] = None  # FIX 1: Changed additional_data to notes

# Schema for creating a new contact. It inherits from the base model.
class ContactCreate(ContactBase):
    pass

# Schema for updating an existing contact. All fields are now optional.
class ContactUpdate(BaseModel): # FIX 2: ContactUpdate no longer inherits directly from ContactBase
    first_name: Optional[str] = Field(None, min_length=2, max_length=50)
    last_name: Optional[str] = Field(None, min_length=2, max_length=50)
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    birthday: Optional[date] = None
    notes: Optional[str] = None

# Schema for the API response. It includes the ID and other fields.
class ContactResponse(ContactBase):
    id: int

    class Config:
        # This parameter allows Pydantic to work with SQLAlchemy ORM models
        from_attributes = True
