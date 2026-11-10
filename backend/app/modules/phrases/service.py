"""
Phrase Service
==============
Business logic for managing saved/favourite phrases.
"""

from typing import List
from fastapi import HTTPException, status

from app.repositories.phrase_repository import PhraseRepository
from app.schemas.phrase import PhraseCreate, PhraseUpdate, PhraseResponse


class PhraseService:
    def __init__(self, phrase_repo: PhraseRepository):
        self._repo = phrase_repo

    async def list_phrases(self, user_id: str) -> List[PhraseResponse]:
        phrases = await self._repo.find_all_by_user(user_id)
        return [PhraseResponse(**p) for p in phrases]

    async def create_phrase(self, user_id: str, data: PhraseCreate) -> PhraseResponse:
        phrase = await self._repo.create(user_id, data.model_dump())
        return PhraseResponse(**phrase)

    async def update_phrase(self, phrase_id: str, user_id: str, data: PhraseUpdate) -> PhraseResponse:
        updates = data.model_dump(exclude_none=True)
        updated = await self._repo.update(phrase_id, user_id, updates)
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "RESOURCE_NOT_FOUND", "message": "Phrase not found"},
            )
        return PhraseResponse(**updated)

    async def delete_phrase(self, phrase_id: str, user_id: str) -> None:
        deleted = await self._repo.soft_delete(phrase_id, user_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "RESOURCE_NOT_FOUND", "message": "Phrase not found"},
            )
