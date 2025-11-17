"""
Live room models for streaming and chat.
"""
import enum
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Enum, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class RoomStatus(str, enum.Enum):
    """Live room status."""
    CREATED = "CREATED"
    LIVE = "LIVE"
    ENDED = "ENDED"


class LiveRoom(Base):
    """Live streaming room where host broadcasts to viewers."""

    __tablename__ = "live_rooms"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    host_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Enum(RoomStatus), default=RoomStatus.CREATED, nullable=False, index=True)

    # LiveKit/Agora room identifier
    provider_room_id = Column(String(255), nullable=True, unique=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    started_at = Column(DateTime, nullable=True)
    ended_at = Column(DateTime, nullable=True)

    # Relationships
    host = relationship("User", back_populates="hosted_rooms", foreign_keys=[host_user_id])
    messages = relationship("LiveRoomMessage", back_populates="room", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<LiveRoom {self.title} ({self.status})>"


class LiveRoomMessage(Base):
    """Chat messages in a live room."""

    __tablename__ = "live_room_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    room_id = Column(UUID(as_uuid=True), ForeignKey("live_rooms.id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    message_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    room = relationship("LiveRoom", back_populates="messages")
    user = relationship("User", back_populates="room_messages")

    def __repr__(self):
        return f"<LiveRoomMessage {self.id}>"
