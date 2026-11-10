"""
FastAPI Dependencies
====================
Reusable FastAPI Depends() callables for auth, database, etc.
"""

from fastapi import Cookie, Depends, Header, HTTPException, status
from jose import JWTError
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.database import get_database
from app.core.security import decode_access_token


async def get_db() -> AsyncIOMotorDatabase:
    """Dependency: returns the active MongoDB database."""
    return get_database()


async def get_current_user_id(
    access_token: str | None = Cookie(default=None),
    authorization: str | None = Header(default=None),
) -> str:
    """
    Dependency: extracts and validates the user ID from:
    1. HttpOnly JWT cookie ("access_token")
    2. Authorization header ("Bearer <token>")
    Raises 401 if missing, expired, or invalid.
    """
    token = access_token
    if not token and authorization:
        parts = authorization.split()
        if len(parts) == 2 and parts[0].lower() == "bearer":
            token = parts[1]
        elif len(parts) == 1:
            token = parts[0]

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated. Provide session cookie or Authorization Bearer token.",
        )
    try:
        payload = decode_access_token(token)
        user_id: str | None = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
            )
        return user_id
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalid or expired",
        )
