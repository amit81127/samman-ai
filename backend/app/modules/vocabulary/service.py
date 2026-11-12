"""
Vocabulary Service
==================
Business logic for vocabulary tile management.
"""

from typing import List
from fastapi import HTTPException, status

from app.core.cache import cache
from app.repositories.board_repository import BoardRepository
from app.repositories.vocabulary_repository import VocabularyRepository
from app.schemas.vocabulary import VocabItemCreate, VocabItemUpdate, VocabItemResponse


class VocabularyService:
    def __init__(self, board_repo: BoardRepository, vocab_repo: VocabularyRepository):
        self._boards = board_repo
        self._vocab = vocab_repo

    async def _verify_board_ownership(self, board_id: str, user_id: str) -> None:
        board = await self._boards.find_by_id(board_id, user_id)
        if not board:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "RESOURCE_NOT_FOUND", "message": "Board not found"},
            )

    async def _get_item_or_404(self, item_id: str, user_id: str) -> dict:
        item = await self._vocab.find_by_id(item_id, user_id)
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "RESOURCE_NOT_FOUND", "message": "Vocabulary item not found"},
            )
        return item

    async def list_items(self, board_id: str, user_id: str) -> List[VocabItemResponse]:
        await self._verify_board_ownership(board_id, user_id)
        items = await self._vocab.find_by_board(board_id, user_id)
        return [VocabItemResponse(**item) for item in items]

    async def create_item(self, board_id: str, user_id: str, data: VocabItemCreate) -> VocabItemResponse:
        await self._verify_board_ownership(board_id, user_id)
        item = await self._vocab.create(board_id, user_id, data.model_dump())
        await cache.invalidate_user_boards(user_id)
        return VocabItemResponse(**item)

    async def update_item(self, item_id: str, user_id: str, data: VocabItemUpdate) -> VocabItemResponse:
        updates = data.model_dump(exclude_none=True)
        item = await self._vocab.update(item_id, user_id, updates)
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "RESOURCE_NOT_FOUND", "message": "Vocabulary item not found"},
            )
        await cache.invalidate_user_boards(user_id)
        return VocabItemResponse(**item)

    async def delete_item(self, item_id: str, user_id: str) -> None:
        deleted = await self._vocab.soft_delete(item_id, user_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "RESOURCE_NOT_FOUND", "message": "Vocabulary item not found"},
            )
        await cache.invalidate_user_boards(user_id)
