"""
Authentication Schemas
======================
Request and response models for auth endpoints.
"""

from pydantic import BaseModel, EmailStr, Field, field_validator


class RegisterRequest(BaseModel):
    """Body for POST /auth/register"""
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    language: str = Field(default="en", max_length=10)

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


class LoginRequest(BaseModel):
    """Body for POST /auth/login"""
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class AuthUserResponse(BaseModel):
    """Safe user representation — includes token for easy API / Postman client usage."""
    id: str
    email: str
    language: str
    access_token: str | None = None
