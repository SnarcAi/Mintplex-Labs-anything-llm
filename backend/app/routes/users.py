"""
User profile routes.
"""
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get a user's public profile."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return UserResponse.from_orm(user)


@router.patch("/me", response_model=UserResponse)
async def update_my_profile(
    update_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update current user's profile."""
    # Update fields if provided
    if update_data.display_name is not None:
        current_user.display_name = update_data.display_name
    if update_data.bio is not None:
        current_user.bio = update_data.bio
    if update_data.grill_level is not None:
        current_user.grill_level = update_data.grill_level
    if update_data.avatar_url is not None:
        current_user.avatar_url = update_data.avatar_url

    await db.commit()
    await db.refresh(current_user)

    return UserResponse.from_orm(current_user)
