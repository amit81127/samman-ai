"""
Partner Service
===============
Business logic for granting and revoking delegated communication partner permissions.
"""

from typing import List
from bson import ObjectId
from fastapi import HTTPException, status

from app.repositories.partner_repository import PartnerRepository
from app.repositories.user_repository import UserRepository
from app.schemas.partner import PartnerGrantRequest, PartnerPermissionResponse


class PartnerService:
    def __init__(self, partner_repo: PartnerRepository, user_repo: UserRepository):
        self._partners = partner_repo
        self._users = user_repo

    async def list_permissions(self, owner_id: str) -> List[PartnerPermissionResponse]:
        perms = await self._partners.find_by_owner(owner_id)
        return [PartnerPermissionResponse(**p) for p in perms]

    async def grant_permission(
        self, owner_id: str, request: PartnerGrantRequest
    ) -> PartnerPermissionResponse:
        partner_input = request.partner_id.strip()

        # Prevent self-delegation by ID
        if owner_id == partner_input:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": "VALIDATION_ERROR", "message": "Cannot grant partner access to yourself"},
            )

        # Retrieve owner profile to prevent self-delegation by email
        owner = await self._users.find_by_id(owner_id)
        if owner and owner.get("email", "").lower() == partner_input.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": "VALIDATION_ERROR", "message": "Cannot grant partner access to yourself"},
            )

        partner_user = None

        # 1. Check if input is a valid ObjectId
        if ObjectId.is_valid(partner_input):
            partner_user = await self._users.find_by_id(partner_input)

        # 2. Check by email if not found
        if not partner_user and ("@" in partner_input or request.partner_email):
            search_email = (request.partner_email or partner_input).lower()
            partner_user = await self._users.find_by_email(search_email)

        # 3. If partner user does not exist yet, provision an invited partner user record
        if not partner_user:
            if "@" in partner_input:
                partner_email = partner_input.lower()
                partner_name = request.partner_name or partner_input.split("@")[0].replace(".", " ").title()
            else:
                partner_name = request.partner_name or partner_input
                clean_handle = partner_input.lower().replace(" ", ".")
                partner_email = f"{clean_handle}@partner.samaan.ai"

            # Check if this email already exists
            existing = await self._users.find_by_email(partner_email)
            if existing:
                partner_user = existing
            else:
                partner_user = await self._users.create_user(
                    email=partner_email,
                    password_hash="<invited_care_partner>",
                    language="en",
                )
            partner_id = str(partner_user["_id"])
        else:
            partner_id = str(partner_user["_id"])
            partner_email = partner_user.get("email")
            partner_name = request.partner_name or partner_user.get("name") or partner_email.split("@")[0].title()

        doc = await self._partners.grant(
            owner_id=owner_id,
            partner_id=partner_id,
            partner_name=partner_name,
            partner_email=partner_email,
            relationship=request.relationship or "Family member",
            permissions=request.permissions,
            expires_at=request.expires_at,
        )
        return PartnerPermissionResponse(**doc)

    async def revoke_permission(self, permission_id: str, owner_id: str) -> None:
        revoked = await self._partners.revoke(permission_id, owner_id)
        if not revoked:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "RESOURCE_NOT_FOUND", "message": "Permission not found"},
            )
