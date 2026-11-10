"""
User Profile Endpoints
======================
GET   /profile   — Get current user's accessibility preferences
PATCH /profile   — Update accessibility preferences
"""

from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.dependencies import get_db, get_current_user_id
from app.repositories.user_repository import UserRepository
from app.modules.users.service import UserService
from app.schemas.user import ProfileResponse, ProfileUpdate

router = APIRouter()


@router.get(
    "/profile",
    response_model=ProfileResponse,
    summary="Get user accessibility profile",
)
async def get_profile(
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Return the authenticated user's profile and accessibility preferences."""
    service = UserService(UserRepository(db))
    return await service.get_profile(user_id)


@router.patch(
    "/profile",
    response_model=ProfileResponse,
    summary="Update accessibility preferences",
)
async def update_profile(
    update: ProfileUpdate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Partially update accessibility preferences.
    Only provided fields are updated. All fields are optional.
    """
    service = UserService(UserRepository(db))
    return await service.update_profile(user_id, update)
