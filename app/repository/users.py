# app/repository/users.py

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from libgravatar import Gravatar

from app.models.users import User
from app.schemas.users import UserModel


async def get_user_by_email(email: str, db: AsyncSession) -> User | None:
    """
    Retrieves a user from the database by their email address.
    :param email: The email address of the user to retrieve.
    :type email: str
    :param db: The asynchronous database session.
    :type db: AsyncSession
    :return: The user object if found, otherwise None.
    :rtype: User | None
    """
    stmt = select(User).filter_by(email=email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    return user


async def create_user(body: UserModel, db: AsyncSession) -> User:
    """
    Creates a new user in the database.
    :param body: The Pydantic model containing user registration data.
    :type body: UserModel
    :param db: The asynchronous database session.
    :type db: AsyncSession
    :return: The newly created user object.
    :rtype: User
    """
    avatar = None
    try:
        g = Gravatar(body.email)
        avatar = g.get_image()
    except Exception as e:
        print(f"Error getting gravatar: {e}")

    new_user = User(username=body.username, email=body.email, password=body.password, avatar=avatar)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


async def update_token(user: User, token: str | None, db: AsyncSession) -> None:
    """
    Updates the refresh token for a given user in the database.
    :param user: The User object whose token needs to be updated.
    :type user: User
    :param token: The new refresh token (or None to clear it).
    :type token: str | None
    :param db: The asynchronous database session.
    :type db: AsyncSession
    """
    user.refresh_token = token
    await db.commit()


async def update_avatar(email: str, url: str, db: AsyncSession) -> User:
    """
    Updates the avatar URL for a user identified by their email.
    :param email: The email of the user to update.
    :type email: str
    :param url: The new avatar URL.
    :type url: str
    :param db: The asynchronous database session.
    :type db: AsyncSession
    :return: The updated user object.
    :rtype: User
    """
    user = await get_user_by_email(email, db)
    if user:
        user.avatar = url
        await db.commit()
        await db.refresh(user)
    return user


async def confirmed_email(email: str, db: AsyncSession) -> None:
    """
    Marks a user's email as confirmed.
    :param email: The email of the user to confirm.
    :type email: str
    :param db: The asynchronous database session.
    :type db: AsyncSession
    """
    user = await get_user_by_email(email, db)
    if user:
        user.confirmed = True
        await db.commit()


async def update_password(user: User, new_password: str, db: AsyncSession) -> None:
    """
    Updates the password for a user.
    :param user: The User object whose password needs to be updated.
    :type user: User
    :param new_password: The new hashed password.
    :type new_password: str
    :param db: The asynchronous database session.
    :type db: AsyncSession
    """
    user.password = new_password
    await db.commit()

async def confirmed_email(email: str, db: AsyncSession) -> None:
    """
    Marks a user's email as confirmed.
    :param email: The email of the user to confirm.
    :type email: str
    :param db: The asynchronous database session.
    :type db: AsyncSession
    """
    user = await get_user_by_email(email, db)
    if user:
        # Виправлено: використовуємо email_verified замість confirmed
        user.email_verified = True
        await db.commit()
