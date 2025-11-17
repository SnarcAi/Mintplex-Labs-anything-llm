"""
Recipe models for content sharing.
"""
import enum
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer, SmallInteger, ForeignKey, Text, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy import Enum

from app.core.database import Base


class MeatType(str, enum.Enum):
    """Type of meat used in recipe."""
    KOFTE = "KOFTE"      # Meatballs/köfte
    BONFILE = "BONFILE"  # Tenderloin/steak
    BALIK = "BALIK"      # Fish
    TAVUK = "TAVUK"      # Chicken
    OTHER = "OTHER"


class Recipe(Base):
    """Recipe posted by users."""

    __tablename__ = "recipes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    author_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    image_url = Column(String(500), nullable=False)
    meat_type = Column(Enum(MeatType), nullable=False)
    difficulty = Column(SmallInteger, nullable=False)  # 1-3
    like_count = Column(Integer, default=0, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    author = relationship("User", back_populates="recipes")
    likes = relationship("RecipeLike", back_populates="recipe", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Recipe {self.title}>"


class RecipeLike(Base):
    """User likes on recipes."""

    __tablename__ = "recipe_likes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    recipe_id = Column(UUID(as_uuid=True), ForeignKey("recipes.id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    recipe = relationship("Recipe", back_populates="likes")
    user = relationship("User", back_populates="recipe_likes")

    # Ensure one like per user per recipe
    __table_args__ = (
        UniqueConstraint("recipe_id", "user_id", name="uq_recipe_user_like"),
        Index("idx_recipe_likes_recipe_user", "recipe_id", "user_id"),
    )

    def __repr__(self):
        return f"<RecipeLike recipe={self.recipe_id} user={self.user_id}>"
