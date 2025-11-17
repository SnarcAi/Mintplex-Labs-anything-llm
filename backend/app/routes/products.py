"""
Shop product routes.
"""
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.product import ShopProduct, ProductCategory
from app.schemas.product import ProductResponse, ProductListResponse

router = APIRouter(prefix="/shop/products", tags=["shop"])


@router.get("", response_model=ProductListResponse)
async def get_products(
    category: Optional[ProductCategory] = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """Get list of shop products."""
    # Build query
    query = select(ShopProduct).where(ShopProduct.is_active == True)

    if category:
        query = query.where(ShopProduct.category == category)

    query = query.limit(limit).offset(offset)

    # Execute query
    result = await db.execute(query)
    products = result.scalars().all()

    # Count total
    count_query = select(func.count(ShopProduct.id)).where(ShopProduct.is_active == True)
    if category:
        count_query = count_query.where(ShopProduct.category == category)

    count_result = await db.execute(count_query)
    total = count_result.scalar()

    return ProductListResponse(
        products=[ProductResponse.from_orm(p) for p in products],
        total=total,
    )


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get a specific product."""
    result = await db.execute(
        select(ShopProduct).where(ShopProduct.id == product_id)
    )
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    return ProductResponse.from_orm(product)
