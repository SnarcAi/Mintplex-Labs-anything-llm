"""
User model and related enums.
"""
import enum
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class GrillLevel(str, enum.Enum):
    """User grill skill levels."""
    CAYLAK = "CAYLAK"  # Beginner
    AMATOR = "AMATOR"  # Amateur
    USTA = "USTA"      # Master


class User(Base):
    """User model for authentication and profiles."""

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    display_name = Column(String(100), nullable=False)
    avatar_url = Column(String(500), nullable=True)
    bio = Column(String(500), nullable=True)
    grill_level = Column(Enum(GrillLevel), default=GrillLevel.CAYLAK, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    hosted_rooms = relationship("LiveRoom", back_populates="host", foreign_keys="LiveRoom.host_user_id")
    room_messages = relationship("LiveRoomMessage", back_populates="user")
    recipes = relationship("Recipe", back_populates="author")
    recipe_likes = relationship("RecipeLike", back_populates="user")

    def __repr__(self):
        return f"<User {self.email}>"
