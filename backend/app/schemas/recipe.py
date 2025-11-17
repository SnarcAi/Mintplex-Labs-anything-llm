"""
Recipe-related Pydantic schemas.
"""
from typing import List, Optional
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field

from app.models.recipe import MeatType
from app.schemas.user import UserResponse


class RecipeCreate(BaseModel):
    """Schema for creating a recipe."""
    title: str = Field(..., min_length=3, max_length=200)
    description: str = Field(..., min_length=10, max_length=1000)
    image_url: str
    meat_type: MeatType
    difficulty: int = Field(..., ge=1, le=3)


class RecipeResponse(BaseModel):
    """Schema for recipe response."""
    id: UUID
    author_user_id: UUID
    author: UserResponse
    title: str
    description: str
    image_url: str
    meat_type: MeatType
    difficulty: int
    like_count: int
    created_at: datetime
    is_liked: Optional[bool] = False  # Whether current user has liked

    class Config:
        from_attributes = True


class RecipeListResponse(BaseModel):
    """Schema for list of recipes."""
    recipes: List[RecipeResponse]
    total: int
