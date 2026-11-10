"""
Auth Service
============
Business logic for registration, login, and logout.
Coordinates UserRepository and security utilities.
"""

import logging
from fastapi import HTTPException, status
from pymongo.errors import DuplicateKeyError

from app.core.security import hash_password, verify_password, create_access_token
from app.repositories.user_repository import UserRepository
from app.schemas.auth import RegisterRequest, LoginRequest, AuthUserResponse

logger = logging.getLogger(__name__)


class AuthService:
    def __init__(self, user_repo: UserRepository):
        self._repo = user_repo

    async def register(self, request: RegisterRequest) -> tuple[AuthUserResponse, str]:
        """
        Register a new user.
        Returns (user_response, access_token).
        Raises 409 if email already exists.
        """
        password_hash = hash_password(request.password)
        try:
            user = await self._repo.create_user(
                email=request.email,
                password_hash=password_hash,
                language=request.language,
            )
        except DuplicateKeyError:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"code": "EMAIL_ALREADY_EXISTS", "message": "Email is already registered"},
            )

        user_id = str(user["_id"])
        token = create_access_token({"sub": user_id})
        response = AuthUserResponse(
            id=user_id,
            email=user["email"],
            language=request.language,
            access_token=token,
        )
        return response, token

    async def login(self, request: LoginRequest) -> tuple[AuthUserResponse, str]:
        """
        Authenticate a user.
        Returns (user_response, access_token).
        Raises 401 on invalid credentials — same message for both wrong
        email and wrong password to prevent user enumeration.
        """
        user = await self._repo.find_by_email(request.email)
        if not user or not verify_password(request.password, user["password_hash"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"code": "INVALID_CREDENTIALS", "message": "Invalid email or password"},
            )

        if not user.get("is_active", True):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"code": "ACCOUNT_DISABLED", "message": "Account is disabled"},
            )

        user_id = str(user["_id"])
        profile = await self._repo.get_profile(user_id)
        language = profile.get("language", "en") if profile else "en"

        token = create_access_token({"sub": user_id})
        response = AuthUserResponse(
            id=user_id,
            email=user["email"],
            language=language,
            access_token=token,
        )
        return response, token
