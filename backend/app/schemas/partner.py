"""
Partner Permission Schemas
==========================
Pydantic models for delegated access permissions.
"""

from datetime import datetime
from typing import List, Literal, Optional, Union
from pydantic import BaseModel, Field

PartnerPermissionType = Literal["view_boards", "assist_compose", "view_history"]


class PartnerGrantRequest(BaseModel):
    partner_id: str = Field(description="Partner user ID, email address, or name")
    partner_name: Optional[str] = Field(default=None, description="Display name for partner")
    partner_email: Optional[str] = Field(default=None, description="Contact email for partner")
    relationship: Optional[str] = Field(default="Family member", description="Care relationship")
    permissions: List[PartnerPermissionType] = Field(min_length=1)
    expires_at: datetime = Field(description="Mandatory expiration timestamp (UTC)")


class PartnerPermissionResponse(BaseModel):
    id: str
    owner_id: str
    partner_id: str
    partner_name: Optional[str] = None
    partner_email: Optional[str] = None
    relationship: Optional[str] = "Family member"
    permissions: List[str]
    granted_at: Union[str, datetime] = ""
    expires_at: Union[str, datetime] = ""
    is_active: bool
