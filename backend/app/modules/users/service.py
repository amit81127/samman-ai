"""
User Service
============
Business logic for user profile and accessibility preferences.
"""

from fastapi import HTTPException, status

from app.repositories.user_repository import UserRepository
from app.schemas.user import ProfileResponse, ProfileUpdate


class UserService:
    def __init__(self, user_repo: UserRepository):
        self._repo = user_repo

    async def get_profile(self, user_id: str) -> ProfileResponse:
        profile = await self._repo.get_profile(user_id)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "RESOURCE_NOT_FOUND", "message": "Profile not found"},
            )
        return ProfileResponse(
            user_id=user_id,
            language=profile.get("language", "en"),
            voice_preference=profile.get("voice_preference"),
            gnani_api_key=profile.get("gnani_api_key"),
            tile_size=profile.get("tile_size", "medium"),
            text_size=profile.get("text_size", "normal"),
            contrast_mode=profile.get("contrast_mode", False),
            reduced_motion=profile.get("reduced_motion", False),
        )

    async def update_profile(self, user_id: str, update: ProfileUpdate) -> ProfileResponse:
        updates = update.model_dump(exclude_none=True)
        if not updates:
            return await self.get_profile(user_id)
        profile = await self._repo.update_profile(user_id, updates)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "RESOURCE_NOT_FOUND", "message": "Profile not found"},
            )
        return ProfileResponse(
            user_id=user_id,
            language=profile.get("language", "en"),
            voice_preference=profile.get("voice_preference"),
            gnani_api_key=profile.get("gnani_api_key"),
            tile_size=profile.get("tile_size", "medium"),
            text_size=profile.get("text_size", "normal"),
            contrast_mode=profile.get("contrast_mode", False),
            reduced_motion=profile.get("reduced_motion", False),
        )
