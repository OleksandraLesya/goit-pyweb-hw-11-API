# app/models/contacts.py

from sqlalchemy import Column, Integer, String, Date, Boolean
from app.database.db import Base


class Contact(Base):
    """
    SQLAlchemy model for contacts.

    This class defines the structure of the 'contacts' table in the database.
    Each instance of this class will represent a single row in the table.
    """
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(50), index=True, nullable=False)
    last_name = Column(String(50), index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    phone_number = Column(String(20), unique=True, nullable=True)
    birthday = Column(Date, nullable=False)
    notes = Column(String(255), nullable=True)
