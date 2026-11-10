"""
Vocabulary Item Endpoints
=========================
PATCH  /vocabulary/{item_id}  — Update a tile
DELETE /vocabulary/{item_id}  — Remove a tile
"""

from fastapi import APIRouter, Depends, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.dependencies import get_db, get_current_user_id
from app.repositories.board_repository import BoardRepository
from app.repositories.vocabulary_repository import VocabularyRepository
from app.modules.vocabulary.service import VocabularyService
from app.schemas.vocabulary import VocabItemUpdate, VocabItemResponse

router = APIRouter()


def _service(db: AsyncIOMotorDatabase) -> VocabularyService:
    return VocabularyService(BoardRepository(db), VocabularyRepository(db))


@router.patch("/{item_id}", response_model=VocabItemResponse, summary="Update a vocabulary tile")
async def update_vocab_item(
    item_id: str,
    data: VocabItemUpdate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    return await _service(db).update_item(item_id, user_id, data)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a vocabulary tile")
async def delete_vocab_item(
    item_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    await _service(db).delete_item(item_id, user_id)
