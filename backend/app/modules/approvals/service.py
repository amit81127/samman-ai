"""
Approval Service
================
Business logic for the message approval workflow.
This is the most safety-critical service in the system.

Invariant: Only approved messages (verified here) may be sent to TTS.
"""

import logging
from fastapi import HTTPException, status

from app.repositories.message_repository import MessageRepository
from app.schemas.approval import ApproveRequest, ApprovalResponse

logger = logging.getLogger(__name__)


class ApprovalService:
    def __init__(self, message_repo: MessageRepository):
        self._messages = message_repo

    async def approve(
        self, message_id: str, user_id: str, request: ApproveRequest
    ) -> ApprovalResponse:
        """
        Record explicit user approval of a specific text.

        Rules enforced:
        - Message must exist and belong to this user
        - Approved text must match candidate text or be user-edited text
        - If candidate_id is specified, it must belong to this message and be passed
        - Version increments on every approval
        - Any future text change will invalidate this approval
        """
        message = await self._messages.find_by_id(message_id, user_id)
        if not message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "RESOURCE_NOT_FOUND", "message": "Message not found"},
            )

        # If a candidate_id is given, verify it exists and is passed
        if request.candidate_id:
            candidate = next(
                (c for c in message.get("candidates", [])
                 if c.get("candidate_id") == request.candidate_id),
                None,
            )
            if not candidate:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={"code": "VALIDATION_ERROR", "message": "Candidate not found in this message"},
                )
            if candidate.get("validation_status") != "passed":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "code": "VALIDATION_ERROR",
                        "message": "Cannot approve a candidate that failed validation",
                    },
                )

        updated = await self._messages.approve(
            message_id=message_id,
            user_id=user_id,
            approved_text=request.approved_text,
            candidate_id=request.candidate_id,
        )
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"code": "INTERNAL_ERROR", "message": "Failed to save approval"},
            )

        logger.info("Message %s approved by user %s (version %d)", message_id, user_id, updated["version"])
        return ApprovalResponse(
            message_id=message_id,
            approved_text=updated["approved_text"],
            approval_status=updated["approval_status"],
            version=updated["version"],
            approved_at=updated.get("approved_at", ""),
        )

    async def invalidate(self, message_id: str, user_id: str) -> None:
        """Allow user to withdraw approval and re-edit."""
        found = await self._messages.invalidate_approval(message_id, user_id)
        if not found:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "RESOURCE_NOT_FOUND", "message": "Message not found"},
            )
