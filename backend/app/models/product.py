"""
Shop product model.
"""
import enum
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Numeric, Boolean, Text, Enum
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class ProductCategory(str, enum.Enum):
    """Product categories."""
    GRILL = "GRILL"
    FUEL = "FUEL"
    ACCESSORY = "ACCESSORY"
    BUNDLE = "BUNDLE"


class ShopProduct(Base):
    """Product catalog for MissYak shop."""

    __tablename__ = "shop_products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    image_url = Column(String(500), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), default="TRY", nullable=False)
    category = Column(Enum(ProductCategory), nullable=False, index=True)
    external_url = Column(String(500), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False, index=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<ShopProduct {self.name}>"
