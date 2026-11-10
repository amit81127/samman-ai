"""
Approval Schemas
================
Request and response models for the approval workflow.
"""

from pydantic import BaseModel, Field


class ApproveRequest(BaseModel):
    """
    Body for POST /messages/{id}/approve.
    Either approve an existing candidate or provide custom edited text.
    """
    candidate_id: str | None = Field(
        default=None,
        description="ID of the AI candidate being approved. Null if approving literal or edited text."
    )
    approved_text: str = Field(
        min_length=1,
        max_length=2000,
        description="The exact text the user is approving. Must match candidate text or be edited text."
    )


class ApprovalResponse(BaseModel):
    """Returned after a successful approval."""
    message_id: str
    approved_text: str
    approval_status: str
    version: int
    approved_at: str
