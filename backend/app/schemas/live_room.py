"""
Live room-related Pydantic schemas.
"""
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field

from app.models.live_room import RoomStatus
from app.schemas.user import UserResponse


class LiveRoomCreate(BaseModel):
    """Schema for creating a live room."""
    title: str = Field(..., min_length=3, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)


class LiveRoomResponse(BaseModel):
    """Schema for live room response."""
    id: UUID
    host_user_id: UUID
    host: UserResponse
    title: str
    description: Optional[str]
    status: RoomStatus
    provider_room_id: Optional[str]
    created_at: datetime
    started_at: Optional[datetime]
    ended_at: Optional[datetime]
    viewer_count: Optional[int] = 0  # Can be populated dynamically

    class Config:
        from_attributes = True


class LiveRoomListResponse(BaseModel):
    """Schema for list of live rooms."""
    rooms: List[LiveRoomResponse]
    total: int


class LiveRoomMessageCreate(BaseModel):
    """Schema for creating a room message."""
    message_text: str = Field(..., min_length=1, max_length=500)


class LiveRoomMessageResponse(BaseModel):
    """Schema for room message response."""
    id: UUID
    room_id: UUID
    user_id: UUID
    user: UserResponse
    message_text: str
    created_at: datetime

    class Config:
        from_attributes = True


class LiveRoomTokenResponse(BaseModel):
    """Schema for LiveKit token response."""
    token: str
    room_name: str
    ws_url: str
