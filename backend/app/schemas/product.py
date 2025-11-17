"""
Product-related Pydantic schemas.
"""
from typing import List
from datetime import datetime
from uuid import UUID
from decimal import Decimal
from pydantic import BaseModel

from app.models.product import ProductCategory


class ProductResponse(BaseModel):
    """Schema for product response."""
    id: UUID
    name: str
    description: str
    image_url: str
    price: Decimal
    currency: str
    category: ProductCategory
    external_url: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ProductListResponse(BaseModel):
    """Schema for list of products."""
    products: List[ProductResponse]
    total: int
