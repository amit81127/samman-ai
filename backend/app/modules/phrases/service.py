"""
Phrase Service
==============
Business logic for managing saved/favourite phrases.
"""

from typing import List
from fastapi import HTTPException, status

from app.core.cache import cache
from app.repositories.phrase_repository import PhraseRepository
from app.schemas.phrase import PhraseCreate, PhraseUpdate, PhraseResponse


class PhraseService:
    def __init__(self, phrase_repo: PhraseRepository):
        self._repo = phrase_repo

    async def list_phrases(self, user_id: str, limit: int = 50, cursor: str | None = None) -> List[PhraseResponse]:
        if cursor:
            # Paged requests bypass primary cache
            phrases = await self._repo.find_all_by_user(user_id, limit=limit, cursor=cursor)
            return [PhraseResponse(**p) for p in phrases]

        async def _fetch():
            return await self._repo.find_all_by_user(user_id, limit=limit, cursor=None)

        cached_phrases = await cache.cache_get_or_set(
            "phrases",
            f"{user_id}:list_{limit}",
            _fetch,
            ttl=300,
        )
        return [PhraseResponse(**p) for p in cached_phrases]

    async def create_phrase(self, user_id: str, data: PhraseCreate) -> PhraseResponse:
        phrase = await self._repo.create(user_id, data.model_dump())
        await cache.invalidate_user_phrases(user_id)
        return PhraseResponse(**phrase)

    async def update_phrase(self, phrase_id: str, user_id: str, data: PhraseUpdate) -> PhraseResponse:
        updates = data.model_dump(exclude_none=True)
        updated = await self._repo.update(phrase_id, user_id, updates)
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "RESOURCE_NOT_FOUND", "message": "Phrase not found"},
            )
        await cache.invalidate_user_phrases(user_id)
        return PhraseResponse(**updated)

    async def delete_phrase(self, phrase_id: str, user_id: str) -> None:
        deleted = await self._repo.soft_delete(phrase_id, user_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "RESOURCE_NOT_FOUND", "message": "Phrase not found"},
            )
        await cache.invalidate_user_phrases(user_id)
