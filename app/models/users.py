# app/models/users.py

from sqlalchemy import Column, Integer, String, DateTime, func, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey
from app.database.db import Base # Ensure Base is imported from app.database.db


class User(Base):
    """
    SQLAlchemy model for users.

    This class defines the structure of the 'users' table in the database.
    It includes fields for user authentication and profile information.
    """
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(250), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    created_at = Column('created_at', DateTime, default=func.now())
    avatar = Column(String(255), nullable=True)
    refresh_token = Column(String(255), nullable=True)

    # Optional: if you want to link notes and tags directly to the user model
    # notes = relationship("Note", backref="user")
    # tags = relationship("Tag", backref="user")
