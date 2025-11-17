"""
Recipe routes for content sharing.
"""
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.deps import get_current_user, get_current_user_optional
from app.models.user import User
from app.models.recipe import Recipe, RecipeLike
from app.schemas.recipe import RecipeCreate, RecipeResponse, RecipeListResponse

router = APIRouter(prefix="/recipes", tags=["recipes"])


@router.post("", response_model=RecipeResponse, status_code=status.HTTP_201_CREATED)
async def create_recipe(
    recipe_data: RecipeCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new recipe."""
    recipe = Recipe(
        author_user_id=current_user.id,
        title=recipe_data.title,
        description=recipe_data.description,
        image_url=recipe_data.image_url,
        meat_type=recipe_data.meat_type,
        difficulty=recipe_data.difficulty,
    )

    db.add(recipe)
    await db.commit()
    await db.refresh(recipe, ["author"])

    response = RecipeResponse.from_orm(recipe)
    response.is_liked = False
    return response


@router.get("", response_model=RecipeListResponse)
async def get_recipes(
    sort: str = Query("latest", regex="^(latest|top)$"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
):
    """Get list of recipes."""
    # Build query
    query = select(Recipe).options(selectinload(Recipe.author))

    if sort == "top":
        # Top recipes by like count
        query = query.order_by(desc(Recipe.like_count), desc(Recipe.created_at))
    else:
        # Latest recipes
        query = query.order_by(desc(Recipe.created_at))

    query = query.limit(limit).offset(offset)

    # Execute query
    result = await db.execute(query)
    recipes = result.scalars().all()

    # Get user's liked recipes if authenticated
    liked_recipe_ids = set()
    if current_user:
        likes_result = await db.execute(
            select(RecipeLike.recipe_id).where(RecipeLike.user_id == current_user.id)
        )
        liked_recipe_ids = {like_id for (like_id,) in likes_result.all()}

    # Build responses
    recipe_responses = []
    for recipe in recipes:
        response = RecipeResponse.from_orm(recipe)
        response.is_liked = recipe.id in liked_recipe_ids
        recipe_responses.append(response)

    # Count total
    count_result = await db.execute(select(func.count(Recipe.id)))
    total = count_result.scalar()

    return RecipeListResponse(
        recipes=recipe_responses,
        total=total,
    )


@router.get("/{recipe_id}", response_model=RecipeResponse)
async def get_recipe(
    recipe_id: UUID,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific recipe."""
    result = await db.execute(
        select(Recipe)
        .where(Recipe.id == recipe_id)
        .options(selectinload(Recipe.author))
    )
    recipe = result.scalar_one_or_none()

    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found",
        )

    response = RecipeResponse.from_orm(recipe)

    # Check if user has liked
    if current_user:
        like_result = await db.execute(
            select(RecipeLike).where(
                RecipeLike.recipe_id == recipe_id,
                RecipeLike.user_id == current_user.id,
            )
        )
        response.is_liked = like_result.scalar_one_or_none() is not None
    else:
        response.is_liked = False

    return response


@router.post("/{recipe_id}/like", status_code=status.HTTP_204_NO_CONTENT)
async def like_recipe(
    recipe_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Like a recipe."""
    # Check if recipe exists
    recipe_result = await db.execute(select(Recipe).where(Recipe.id == recipe_id))
    recipe = recipe_result.scalar_one_or_none()

    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found",
        )

    # Check if already liked
    like_result = await db.execute(
        select(RecipeLike).where(
            RecipeLike.recipe_id == recipe_id,
            RecipeLike.user_id == current_user.id,
        )
    )
    existing_like = like_result.scalar_one_or_none()

    if existing_like:
        # Already liked, do nothing (idempotent)
        return

    # Create like
    like = RecipeLike(
        recipe_id=recipe_id,
        user_id=current_user.id,
    )
    db.add(like)

    # Increment like count
    recipe.like_count += 1

    await db.commit()


@router.delete("/{recipe_id}/like", status_code=status.HTTP_204_NO_CONTENT)
async def unlike_recipe(
    recipe_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Unlike a recipe."""
    # Check if recipe exists
    recipe_result = await db.execute(select(Recipe).where(Recipe.id == recipe_id))
    recipe = recipe_result.scalar_one_or_none()

    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found",
        )

    # Find and delete like
    like_result = await db.execute(
        select(RecipeLike).where(
            RecipeLike.recipe_id == recipe_id,
            RecipeLike.user_id == current_user.id,
        )
    )
    like = like_result.scalar_one_or_none()

    if not like:
        # Not liked, do nothing (idempotent)
        return

    await db.delete(like)

    # Decrement like count
    if recipe.like_count > 0:
        recipe.like_count -= 1

    await db.commit()
