"""
Board Service
=============
Business logic for board management.
Enforces ownership — users can only access their own boards.
"""

from typing import List
from fastapi import HTTPException, status

from app.core.cache import cache
from app.repositories.board_repository import BoardRepository
from app.repositories.vocabulary_repository import VocabularyRepository
from app.schemas.board import BoardCreate, BoardUpdate, BoardResponse


class BoardService:
    def __init__(self, board_repo: BoardRepository, vocab_repo: VocabularyRepository):
        self._boards = board_repo
        self._vocab = vocab_repo

    async def _get_or_404(self, board_id: str, user_id: str) -> dict:
        board = await self._boards.find_by_id(board_id, user_id)
        if not board:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "RESOURCE_NOT_FOUND", "message": "Board not found"},
            )
        return board

    async def _enrich(self, board: dict, user_id: str) -> BoardResponse:
        count = await self._vocab.count_by_board(board["id"], user_id)
        return BoardResponse(**board, tile_count=count)

    async def list_boards(self, user_id: str) -> List[BoardResponse]:
        async def _fetch():
            boards = await self._boards.find_all_with_tile_counts(user_id)
            if not boards:
                # Seed standard starter boards for new user in MongoDB
                starter_definitions = [
                    {
                        "name": "Daily needs",
                        "description": "Everyday personal and comfort essentials",
                        "categories": ["Basic needs", "Everyday"],
                        "is_default": True,
                    },
                    {
                        "name": "Health & Care",
                        "description": "Medical communication, pain symptoms, and therapy",
                        "categories": ["Health", "Feelings"],
                        "is_default": False,
                    },
                    {
                        "name": "School & Learning",
                        "description": "Classroom interaction, subjects, and questions",
                        "categories": ["People", "Actions"],
                        "is_default": False,
                    },
                    {
                        "name": "Quick communication",
                        "description": "Instant greetings, confirmations, and alerts",
                        "categories": ["Actions", "Basic needs"],
                        "is_default": False,
                    },
                ]
                for s in starter_definitions:
                    await self._boards.create(user_id, s)
                boards = await self._boards.find_all_with_tile_counts(user_id)
            return boards

        # Two-level cache lookup with anti-stampede lock
        cached_boards = await cache.cache_get_or_set(
            "boards",
            f"{user_id}:list",
            _fetch,
            ttl=300,
        )
        return [BoardResponse(**b) for b in cached_boards]

    async def create_board(self, user_id: str, data: BoardCreate) -> BoardResponse:
        board = await self._boards.create(user_id, data.model_dump())
        await cache.invalidate_user_boards(user_id)
        return BoardResponse(**board, tile_count=0)

    async def get_board(self, board_id: str, user_id: str) -> BoardResponse:
        board = await self._get_or_404(board_id, user_id)
        return await self._enrich(board, user_id)

    async def update_board(self, board_id: str, user_id: str, data: BoardUpdate) -> BoardResponse:
        updates = data.model_dump(exclude_none=True)
        board = await self._boards.update(board_id, user_id, updates)
        if not board:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "RESOURCE_NOT_FOUND", "message": "Board not found"},
            )
        await cache.invalidate_user_boards(user_id)
        return await self._enrich(board, user_id)

    async def delete_board(self, board_id: str, user_id: str) -> None:
        deleted = await self._boards.soft_delete(board_id, user_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "RESOURCE_NOT_FOUND", "message": "Board not found"},
            )
        await cache.invalidate_user_boards(user_id)
