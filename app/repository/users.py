# app/repository/users.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from libgravatar import Gravatar

from app.models.users import User
from app.schemas.users import UserModel


async def get_user_by_email(email: str, db: AsyncSession) -> User | None:
    """
    Retrieves a user from the database by their email address.

    :param email: The email address of the user to retrieve.
    :param db: The asynchronous database session.
    :return: The User object if found, otherwise None.
    """
    stmt = select(User).filter_by(email=email)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def create_user(body: UserModel, db: AsyncSession) -> User:
    """
    Creates a new user in the database.

    :param body: The Pydantic model containing user registration data.
    :param db: The asynchronous database session.
    :return: The newly created User object.
    """
    avatar = None
    try:
        g = Gravatar(body.email)
        avatar = g.get_image()
    except Exception as e:
        print(f"Error getting gravatar: {e}") # Log the error for debugging

    new_user = User(email=body.email, password=body.password, avatar=avatar)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


async def update_token(user: User, token: str | None, db: AsyncSession) -> None:
    """
    Updates the refresh token for a given user in the database.

    :param user: The User object whose token needs to be updated.
    :param token: The new refresh token (or None to clear it).
    :param db: The asynchronous database session.
    :return: None
    """
    user.refresh_token = token
    await db.commit()
