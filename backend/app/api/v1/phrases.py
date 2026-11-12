"""
Phrase Endpoints
================
GET    /phrases        — List saved phrases
POST   /phrases        — Save a phrase
PATCH  /phrases/{id}   — Edit a phrase
DELETE /phrases/{id}   — Delete a phrase
"""

from typing import List
from fastapi import APIRouter, Depends, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.dependencies import get_db, get_current_user_id
from app.repositories.phrase_repository import PhraseRepository
from app.modules.phrases.service import PhraseService
from app.schemas.phrase import PhraseCreate, PhraseUpdate, PhraseResponse

router = APIRouter()


def _service(db: AsyncIOMotorDatabase) -> PhraseService:
    return PhraseService(PhraseRepository(db))


@router.get("", response_model=List[PhraseResponse], summary="List saved phrases")
async def list_phrases(
    limit: int = 50,
    cursor: str | None = None,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    return await _service(db).list_phrases(user_id, limit=limit, cursor=cursor)


@router.post("", response_model=PhraseResponse, status_code=status.HTTP_201_CREATED, summary="Save a phrase")
async def create_phrase(
    data: PhraseCreate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    return await _service(db).create_phrase(user_id, data)


@router.patch("/{phrase_id}", response_model=PhraseResponse, summary="Update a phrase")
async def update_phrase(
    phrase_id: str,
    data: PhraseUpdate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    return await _service(db).update_phrase(phrase_id, user_id, data)


@router.delete("/{phrase_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a phrase")
async def delete_phrase(
    phrase_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    await _service(db).delete_phrase(phrase_id, user_id)
