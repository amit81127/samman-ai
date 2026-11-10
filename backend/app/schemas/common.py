"""
Common Schemas
==============
Shared Pydantic models used across the application:
- Standardised error response envelope
- Pagination metadata
"""

from typing import Any, Generic, TypeVar
from pydantic import BaseModel

DataT = TypeVar("DataT")


class ErrorDetail(BaseModel):
    """Standard error response body."""
    code: str           # Machine-readable error code e.g. "APPROVAL_REQUIRED"
    message: str        # Human-readable description
    field: str | None = None  # Which field caused the error (validation errors)


class ErrorResponse(BaseModel):
    """Envelope for all error responses."""
    error: ErrorDetail


class SuccessResponse(BaseModel, Generic[DataT]):
    """Envelope for successful responses."""
    data: DataT


class PaginationMeta(BaseModel):
    total: int
    page: int
    page_size: int
    has_next: bool


# Common error codes — add new ones here as the app grows
class ErrorCode:
    # Auth
    NOT_AUTHENTICATED = "NOT_AUTHENTICATED"
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    EMAIL_ALREADY_EXISTS = "EMAIL_ALREADY_EXISTS"
    # Authorisation
    FORBIDDEN = "FORBIDDEN"
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
    # Messages / Approval
    APPROVAL_REQUIRED = "APPROVAL_REQUIRED"
    APPROVAL_INVALIDATED = "APPROVAL_INVALIDATED"
    # Validation
    VALIDATION_ERROR = "VALIDATION_ERROR"
    # Providers
    AI_GENERATION_FAILED = "AI_GENERATION_FAILED"
    TTS_FAILED = "TTS_FAILED"
