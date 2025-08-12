# app/routes/users.py

import os
import cloudinary
import cloudinary.uploader
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.db import get_db
from app.models.users import User
from app.repository import users as repository_users
from app.services.auth import auth_service
from app.schemas.users import UserResponse

router = APIRouter(prefix="/users", tags=["users"])

# Configure Cloudinary using environment variables directly
cloudinary.config(
    cloud_name=os.environ.get('CLOUDINARY_NAME'),
    api_key=os.environ.get('CLOUDINARY_API_KEY'),
    api_secret=os.environ.get('CLOUDINARY_API_SECRET'),
    secure=True
)


@router.patch('/avatar', response_model=UserResponse)
async def update_avatar_user(
        file: UploadFile = File(),
        current_user: User = Depends(auth_service.get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """
    Updates the avatar for the current user.

    :param file: The image file to upload as the avatar.
    :type file: UploadFile
    :param current_user: The currently authenticated user.
    :type current_user: User
    :param db: The asynchronous database session.
    :type db: AsyncSession
    :return: The updated user information.
    :rtype: UserResponse
    """
    # Check if the uploaded file is an image
    if not file.content_type.startswith("image"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only image files are allowed")

    # Use a unique public_id for each user's avatar
    public_id = f"contacts-app/{current_user.email}"

    # Upload the file to Cloudinary with specific settings
    res = cloudinary.uploader.upload(file.file, public_id=public_id, overwrite=True)

    # Build a secure URL for the avatar with transformations
    res_url = cloudinary.CloudinaryImage(public_id).build_url(
        width=250,
        height=250,
        crop='fill',
        version=res.get('version'),
        secure=True
    )

    # Update the avatar URL in the database
    user = await repository_users.update_avatar(current_user.email, res_url, db)

    return user
