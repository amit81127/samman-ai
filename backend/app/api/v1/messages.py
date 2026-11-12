"""
Message Endpoints
=================
POST /messages/compose           — Submit concepts, get literal + AI candidates
GET  /messages                   — List recent messages
GET  /messages/{id}              — Get specific message
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.dependencies import get_db, get_current_user_id
from app.repositories.message_repository import MessageRepository
from app.repositories.user_repository import UserRepository
from app.repositories.partner_repository import PartnerRepository
from app.modules.messages.service import MessageService
from app.schemas.message import ComposeRequest, MessageResponse

router = APIRouter()


def _service(db: AsyncIOMotorDatabase) -> MessageService:
    return MessageService(MessageRepository(db), UserRepository(db))


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


@router.post(
    "/compose",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Compose a message — get literal text and AI candidates",
)
async def compose_message(
    request: ComposeRequest,
    owner_id: str | None = None,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Submit selected concepts. Returns:
    - literal_text: deterministic join of concepts (always present)
    - candidates: AI-generated sentence options (only passed-validation ones)
    """
    target_user_id = await _resolve_user_id(owner_id, user_id, db, "assist_compose")
    return await _service(db).compose(target_user_id, request)


@router.get(
    "",
    response_model=List[MessageResponse],
    summary="List recent messages",
)
async def list_messages(
    owner_id: str | None = None,
    limit: int = 20,
    cursor: str | None = None,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    target_user_id = await _resolve_user_id(owner_id, user_id, db, "view_history")
    return await _service(db).list_messages(target_user_id, limit=limit, cursor=cursor)


@router.get(
    "/{message_id}",
    response_model=MessageResponse,
    summary="Get a specific message",
)
async def get_message(
    message_id: str,
    owner_id: str | None = None,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    target_user_id = await _resolve_user_id(owner_id, user_id, db, "view_history")
    return await _service(db).get_message(message_id, target_user_id)
