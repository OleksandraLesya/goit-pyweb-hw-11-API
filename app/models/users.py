# app/models/users.py

from sqlalchemy import Column, Integer, String, DateTime, func, Boolean, Enum
from sqlalchemy.orm import declarative_base
import enum

Base = declarative_base()

class Role(enum.Enum):
    """
    Enum for user roles.
    """
    admin = "admin"
    moderator = "moderator"
    user = "user"


class User(Base):
    """
    SQLAlchemy model for the 'users' table.
    """
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(50), nullable=False, unique=True)  # Додано поле username
    email = Column(String(255), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=func.now())
    avatar = Column(String(255), nullable=True)
    refresh_token = Column(String(255), nullable=True)
    email_verified = Column(Boolean, default=False)
    role = Column(Enum(Role), default=Role.user, nullable=False)

