"""
User-related Pydantic schemas.
"""
from typing import Optional
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field

from app.models.user import GrillLevel


class UserCreate(BaseModel):
    """Schema for user registration."""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    display_name: str = Field(..., min_length=2, max_length=100)
    grill_level: GrillLevel = GrillLevel.CAYLAK


class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    """Schema for updating user profile."""
    display_name: Optional[str] = Field(None, min_length=2, max_length=100)
    bio: Optional[str] = Field(None, max_length=500)
    grill_level: Optional[GrillLevel] = None
    avatar_url: Optional[str] = None


class UserResponse(BaseModel):
    """Schema for user response."""
    id: UUID
    email: EmailStr
    display_name: str
    avatar_url: Optional[str]
    bio: Optional[str]
    grill_level: GrillLevel
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    """Schema for JWT token response."""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
