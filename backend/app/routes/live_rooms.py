"""
Live room routes for streaming and chat.
"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.live_room import LiveRoom, LiveRoomMessage, RoomStatus
from app.schemas.live_room import (
    LiveRoomCreate,
    LiveRoomResponse,
    LiveRoomListResponse,
    LiveRoomMessageCreate,
    LiveRoomMessageResponse,
    LiveRoomTokenResponse,
)
from app.services.livekit_service import livekit_service

router = APIRouter(prefix="/rooms", tags=["live_rooms"])


@router.post("", response_model=LiveRoomResponse, status_code=status.HTTP_201_CREATED)
async def create_room(
    room_data: LiveRoomCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new live room."""
    # Generate LiveKit room name
    provider_room_id = livekit_service.generate_room_name()

    # Create room record
    room = LiveRoom(
        host_user_id=current_user.id,
        title=room_data.title,
        description=room_data.description,
        status=RoomStatus.CREATED,
        provider_room_id=provider_room_id,
    )

    db.add(room)
    await db.commit()
    await db.refresh(room, ["host"])

    return LiveRoomResponse.from_orm(room)


@router.post("/{room_id}/start", response_model=LiveRoomTokenResponse)
async def start_room(
    room_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Start a live room and get host token."""
    # Get room
    result = await db.execute(
        select(LiveRoom).where(LiveRoom.id == room_id)
    )
    room = result.scalar_one_or_none()

    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found",
        )

    # Verify user is host
    if room.host_user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the host can start the room",
        )

    # Update room status
    room.status = RoomStatus.LIVE
    room.started_at = datetime.utcnow()
    await db.commit()

    # Generate host token
    token = livekit_service.create_token(
        room_name=room.provider_room_id,
        participant_name=current_user.display_name,
        is_host=True,
    )

    return LiveRoomTokenResponse(
        token=token,
        room_name=room.provider_room_id,
        ws_url=livekit_service.ws_url,
    )


@router.post("/{room_id}/join", response_model=LiveRoomTokenResponse)
async def join_room(
    room_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Join a live room as a viewer."""
    # Get room
    result = await db.execute(
        select(LiveRoom).where(LiveRoom.id == room_id)
    )
    room = result.scalar_one_or_none()

    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found",
        )

    if room.status != RoomStatus.LIVE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Room is not live",
        )

    # Generate viewer token
    is_host = room.host_user_id == current_user.id
    token = livekit_service.create_token(
        room_name=room.provider_room_id,
        participant_name=current_user.display_name,
        is_host=is_host,
    )

    return LiveRoomTokenResponse(
        token=token,
        room_name=room.provider_room_id,
        ws_url=livekit_service.ws_url,
    )


@router.post("/{room_id}/end", response_model=LiveRoomResponse)
async def end_room(
    room_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """End a live room."""
    # Get room
    result = await db.execute(
        select(LiveRoom).where(LiveRoom.id == room_id).options(selectinload(LiveRoom.host))
    )
    room = result.scalar_one_or_none()

    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found",
        )

    # Verify user is host
    if room.host_user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the host can end the room",
        )

    # Update room status
    room.status = RoomStatus.ENDED
    room.ended_at = datetime.utcnow()
    await db.commit()
    await db.refresh(room)

    # End LiveKit room
    await livekit_service.end_room(room.provider_room_id)

    return LiveRoomResponse.from_orm(room)


@router.get("/live", response_model=LiveRoomListResponse)
async def get_live_rooms(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """Get list of currently live rooms."""
    # Query live rooms
    result = await db.execute(
        select(LiveRoom)
        .where(LiveRoom.status == RoomStatus.LIVE)
        .options(selectinload(LiveRoom.host))
        .order_by(desc(LiveRoom.started_at))
        .limit(limit)
        .offset(offset)
    )
    rooms = result.scalars().all()

    # Count total
    count_result = await db.execute(
        select(LiveRoom).where(LiveRoom.status == RoomStatus.LIVE)
    )
    total = len(count_result.scalars().all())

    return LiveRoomListResponse(
        rooms=[LiveRoomResponse.from_orm(room) for room in rooms],
        total=total,
    )


@router.get("/{room_id}", response_model=LiveRoomResponse)
async def get_room(
    room_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get room details."""
    result = await db.execute(
        select(LiveRoom)
        .where(LiveRoom.id == room_id)
        .options(selectinload(LiveRoom.host))
    )
    room = result.scalar_one_or_none()

    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found",
        )

    return LiveRoomResponse.from_orm(room)


@router.get("/{room_id}/messages", response_model=List[LiveRoomMessageResponse])
async def get_room_messages(
    room_id: UUID,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """Get chat messages for a room."""
    # Verify room exists
    result = await db.execute(select(LiveRoom).where(LiveRoom.id == room_id))
    room = result.scalar_one_or_none()

    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found",
        )

    # Get messages
    messages_result = await db.execute(
        select(LiveRoomMessage)
        .where(LiveRoomMessage.room_id == room_id)
        .options(selectinload(LiveRoomMessage.user))
        .order_by(LiveRoomMessage.created_at)
        .limit(limit)
        .offset(offset)
    )
    messages = messages_result.scalars().all()

    return [LiveRoomMessageResponse.from_orm(msg) for msg in messages]


@router.post("/{room_id}/messages", response_model=LiveRoomMessageResponse, status_code=status.HTTP_201_CREATED)
async def post_room_message(
    room_id: UUID,
    message_data: LiveRoomMessageCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Post a chat message to a room."""
    # Verify room exists and is live
    result = await db.execute(select(LiveRoom).where(LiveRoom.id == room_id))
    room = result.scalar_one_or_none()

    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found",
        )

    if room.status != RoomStatus.LIVE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only post messages to live rooms",
        )

    # Create message
    message = LiveRoomMessage(
        room_id=room_id,
        user_id=current_user.id,
        message_text=message_data.message_text,
    )

    db.add(message)
    await db.commit()
    await db.refresh(message, ["user"])

    return LiveRoomMessageResponse.from_orm(message)
