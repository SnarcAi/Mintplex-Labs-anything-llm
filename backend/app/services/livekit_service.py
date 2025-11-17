"""
LiveKit integration service for video streaming.
"""
import secrets
from datetime import timedelta
from livekit import api

from app.core.config import settings


class LiveKitService:
    """Service for managing LiveKit rooms and tokens."""

    def __init__(self):
        self.api_key = settings.LIVEKIT_API_KEY
        self.api_secret = settings.LIVEKIT_API_SECRET
        self.ws_url = settings.LIVEKIT_WS_URL

    def generate_room_name(self) -> str:
        """Generate a unique room name."""
        return f"room_{secrets.token_urlsafe(16)}"

    def create_token(
        self,
        room_name: str,
        participant_name: str,
        is_host: bool = False,
    ) -> str:
        """
        Create a LiveKit access token for a participant.

        Args:
            room_name: Name of the room
            participant_name: Display name of the participant
            is_host: Whether the participant is the host (can publish video/audio)

        Returns:
            JWT token for LiveKit client
        """
        token = api.AccessToken(self.api_key, self.api_secret)
        token.with_identity(participant_name)
        token.with_name(participant_name)
        token.with_ttl(timedelta(hours=6))

        # Grant permissions
        grants = api.VideoGrants(
            room_join=True,
            room=room_name,
        )

        if is_host:
            # Host can publish video and audio
            grants.can_publish = True
            grants.can_publish_data = True
            grants.can_subscribe = True
        else:
            # Viewers can only subscribe (watch)
            grants.can_publish = False
            grants.can_publish_data = True  # For chat
            grants.can_subscribe = True

        token.with_grants(grants)

        return token.to_jwt()

    async def create_room(self, room_name: str) -> dict:
        """
        Create a LiveKit room (optional - rooms are auto-created on join).

        Args:
            room_name: Name of the room to create

        Returns:
            Room info dict
        """
        # Note: LiveKit auto-creates rooms when participants join
        # This method is here for explicit room creation if needed
        return {
            "name": room_name,
            "ws_url": self.ws_url,
        }

    async def end_room(self, room_name: str):
        """
        End a LiveKit room (disconnect all participants).

        Args:
            room_name: Name of the room to end
        """
        # In production, you might want to use LiveKit API to delete the room
        # For V1, rooms auto-cleanup when all participants leave
        pass


# Singleton instance
livekit_service = LiveKitService()
