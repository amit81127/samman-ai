"""
Approval Endpoints
==================
POST   /messages/{id}/approve    — Approve a candidate or literal text
DELETE /messages/{id}/approval   — Invalidate an approval (user wants to re-edit)
"""

from fastapi import APIRouter, Depends, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.dependencies import get_db, get_current_user_id
from app.repositories.message_repository import MessageRepository
from app.modules.approvals.service import ApprovalService
from app.schemas.approval import ApproveRequest, ApprovalResponse

router = APIRouter()


def _service(db: AsyncIOMotorDatabase) -> ApprovalService:
    return ApprovalService(MessageRepository(db))


@router.post(
    "/{message_id}/approve",
    response_model=ApprovalResponse,
    summary="Approve a message — unlock speech synthesis",
)
async def approve_message(
    message_id: str,
    request: ApproveRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Explicitly approve a specific text for speech synthesis.
    After this, POST /messages/{id}/speech becomes available.
    Any edit to the text invalidates this approval automatically.
    """
    return await _service(db).approve(message_id, user_id, request)


@router.delete(
    "/{message_id}/approval",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Invalidate an approval (user wants to re-edit)",
)
async def invalidate_approval(
    message_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Reset approval status so the user can edit and re-approve."""
    await _service(db).invalidate(message_id, user_id)
