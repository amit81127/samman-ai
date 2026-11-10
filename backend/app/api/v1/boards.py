"""
Board Endpoints
===============
GET    /boards               — List user's boards
POST   /boards               — Create board
GET    /boards/{id}          — Get board with tile count
PATCH  /boards/{id}          — Update board
DELETE /boards/{id}          — Soft-delete board
GET    /boards/{id}/vocabulary — List tiles for board
POST   /boards/{id}/vocabulary — Add tile to board
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.dependencies import get_db, get_current_user_id
from app.repositories.board_repository import BoardRepository
from app.repositories.vocabulary_repository import VocabularyRepository
from app.repositories.partner_repository import PartnerRepository
from app.modules.boards.service import BoardService
from app.modules.vocabulary.service import VocabularyService
from app.schemas.board import BoardCreate, BoardUpdate, BoardResponse
from app.schemas.vocabulary import VocabItemCreate, VocabItemResponse

router = APIRouter()


def _board_service(db: AsyncIOMotorDatabase) -> BoardService:
    return BoardService(BoardRepository(db), VocabularyRepository(db))


def _vocab_service(db: AsyncIOMotorDatabase) -> VocabularyService:
    return VocabularyService(BoardRepository(db), VocabularyRepository(db))


async def _resolve_user_id(owner_id: str | None, current_user_id: str, db: AsyncIOMotorDatabase, required_permission: str) -> str:
    if not owner_id or owner_id == current_user_id:
        return current_user_id
    partner_repo = PartnerRepository(db)
    perm = await partner_repo.find_active_permission(owner_id=owner_id, partner_id=current_user_id)
    if not perm or required_permission not in perm.get("permissions", []):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "FORBIDDEN", "message": f"No active '{required_permission}' permission for this account"},
        )
    return owner_id


@router.get("", response_model=List[BoardResponse], summary="List all boards")
async def list_boards(
    owner_id: str | None = None,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    target_user_id = await _resolve_user_id(owner_id, user_id, db, "view_boards")
    return await _board_service(db).list_boards(target_user_id)


@router.post("", response_model=BoardResponse, status_code=status.HTTP_201_CREATED, summary="Create a board")
async def create_board(
    data: BoardCreate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    return await _board_service(db).create_board(user_id, data)


@router.get("/{board_id}", response_model=BoardResponse, summary="Get a board")
async def get_board(
    board_id: str,
    owner_id: str | None = None,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    target_user_id = await _resolve_user_id(owner_id, user_id, db, "view_boards")
    return await _board_service(db).get_board(board_id, target_user_id)


@router.patch("/{board_id}", response_model=BoardResponse, summary="Update a board")
async def update_board(
    board_id: str,
    data: BoardUpdate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    return await _board_service(db).update_board(board_id, user_id, data)


@router.delete("/{board_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a board")
async def delete_board(
    board_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    await _board_service(db).delete_board(board_id, user_id)


@router.get("/{board_id}/vocabulary", response_model=List[VocabItemResponse], summary="List vocabulary tiles")
async def list_vocab(
    board_id: str,
    owner_id: str | None = None,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    target_user_id = await _resolve_user_id(owner_id, user_id, db, "view_boards")
    return await _vocab_service(db).list_items(board_id, target_user_id)


@router.post("/{board_id}/vocabulary", response_model=VocabItemResponse, status_code=status.HTTP_201_CREATED, summary="Add a vocabulary tile")
async def create_vocab(
    board_id: str,
    data: VocabItemCreate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    return await _vocab_service(db).create_item(board_id, user_id, data)
