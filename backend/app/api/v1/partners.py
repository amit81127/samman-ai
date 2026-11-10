"""
Partner Endpoints
=================
GET    /partners        — List active partner permissions
POST   /partners        — Grant a partner permission
DELETE /partners/{id}   — Revoke a partner's access
"""

from typing import List
from fastapi import APIRouter, Depends, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.dependencies import get_db, get_current_user_id
from app.repositories.partner_repository import PartnerRepository
from app.repositories.user_repository import UserRepository
from app.modules.partners.service import PartnerService
from app.schemas.partner import PartnerGrantRequest, PartnerPermissionResponse

router = APIRouter()


def _service(db: AsyncIOMotorDatabase) -> PartnerService:
    return PartnerService(PartnerRepository(db), UserRepository(db))


@router.get("", response_model=List[PartnerPermissionResponse], summary="List granted partner permissions")
async def list_partners(
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    return await _service(db).list_permissions(user_id)


@router.post("", response_model=PartnerPermissionResponse, status_code=status.HTTP_201_CREATED, summary="Grant partner permission")
async def grant_partner(
    request: PartnerGrantRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    return await _service(db).grant_permission(user_id, request)


@router.delete("/{permission_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Revoke partner permission")
async def revoke_partner(
    permission_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    await _service(db).revoke_permission(permission_id, user_id)
