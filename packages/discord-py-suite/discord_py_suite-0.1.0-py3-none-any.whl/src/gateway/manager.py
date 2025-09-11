"""Gateway manager for Discord real-time events."""

import asyncio
import discord
from loguru import logger
from typing import Any, Dict, List, Optional

from .event_buffer import CircularEventBuffer
from .event_filter import EventFilter


class GatewayManager:
    """Manages Discord Gateway connection and event streaming."""

    def __init__(self, token: str, intents: int) -> None:
        self.token = token
        self.intents = discord.Intents(intents)
        self.client = discord.Client(intents=self.intents)
        self.event_buffer = CircularEventBuffer(maxsize=1000)
        self.event_filter = EventFilter()
        self.is_running = False

        # Set up event handlers
        self._setup_event_handlers()

    def _setup_event_handlers(self) -> None:
        """Set up Discord event handlers."""

        @self.client.event
        async def on_ready() -> None:
            logger.info(f"Gateway connected as {self.client.user}")
            self.is_running = True

        @self.client.event
        async def on_disconnect() -> None:
            logger.warning("Gateway disconnected")

        @self.client.event
        async def on_resumed() -> None:
            logger.info("Gateway connection resumed")

        # Message events
        @self.client.event
        async def on_raw_message_create(payload: Any) -> None:
            await self._handle_raw_event("MESSAGE_CREATE", payload)

        @self.client.event
        async def on_raw_message_update(payload: Any) -> None:
            await self._handle_raw_event("MESSAGE_UPDATE", payload)

        @self.client.event
        async def on_raw_message_delete(payload: Any) -> None:
            await self._handle_raw_event("MESSAGE_DELETE", payload)

        # Reaction events
        @self.client.event
        async def on_raw_reaction_add(payload: Any) -> None:
            await self._handle_raw_event("MESSAGE_REACTION_ADD", payload)

        @self.client.event
        async def on_raw_reaction_remove(payload: Any) -> None:
            await self._handle_raw_event("MESSAGE_REACTION_REMOVE", payload)

        # Guild events
        @self.client.event
        async def on_guild_join(guild: discord.Guild) -> None:
            await self._handle_event(
                "GUILD_CREATE", {"guild": self._format_guild(guild)}
            )

        @self.client.event
        async def on_guild_remove(guild: discord.Guild) -> None:
            await self._handle_event(
                "GUILD_DELETE", {"guild": self._format_guild(guild)}
            )

        # Member events
        @self.client.event
        async def on_member_join(member: discord.Member) -> None:
            await self._handle_event(
                "GUILD_MEMBER_ADD", {"member": self._format_member(member)}
            )

        @self.client.event
        async def on_member_remove(member: discord.Member) -> None:
            await self._handle_event(
                "GUILD_MEMBER_REMOVE", {"member": self._format_member(member)}
            )

        # Channel events
        @self.client.event
        async def on_guild_channel_create(channel: discord.abc.GuildChannel) -> None:
            await self._handle_event(
                "CHANNEL_CREATE", {"channel": self._format_channel(channel)}
            )

        @self.client.event
        async def on_guild_channel_delete(channel: discord.abc.GuildChannel) -> None:
            await self._handle_event(
                "CHANNEL_DELETE", {"channel": self._format_channel(channel)}
            )

    async def _handle_raw_event(self, event_type: str, payload: Any) -> None:
        """Handle raw Discord events."""
        try:
            event = self._format_event(event_type, payload.data)
            if self.event_filter.should_include(event):
                self.event_buffer.add(event)
                logger.debug(f"Buffered event: {event_type}")
        except Exception as e:
            logger.error(f"Error handling raw event {event_type}: {e}")

    async def _handle_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Handle processed Discord events."""
        try:
            event = self._format_event(event_type, data)
            if self.event_filter.should_include(event):
                self.event_buffer.add(event)
                logger.debug(f"Buffered event: {event_type}")
        except Exception as e:
            logger.error(f"Error handling event {event_type}: {e}")

    def _format_event(self, event_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Format event data for consistent structure."""
        return {
            "type": event_type,
            "data": data,
            "gateway": {
                "shard_id": getattr(self.client, "shard_id", 0),
                "user_id": str(self.client.user.id) if self.client.user else None,
            },
        }

    def _format_guild(self, guild: discord.Guild) -> Dict[str, Any]:
        """Format guild object for events."""
        return {
            "id": str(guild.id),
            "name": guild.name,
            "member_count": guild.member_count,
            "owner_id": str(guild.owner_id) if guild.owner_id else None,
        }

    def _format_member(self, member: discord.Member) -> Dict[str, Any]:
        """Format member object for events."""
        return {
            "user": {
                "id": str(member.id),
                "username": member.name,
                "discriminator": member.discriminator,
                "bot": member.bot,
            },
            "guild_id": str(member.guild.id),
            "nick": member.nick,
            "roles": [str(role.id) for role in member.roles],
        }

    def _format_channel(self, channel: discord.abc.GuildChannel) -> Dict[str, Any]:
        """Format channel object for events."""
        return {
            "id": str(channel.id),
            "name": getattr(channel, "name", None),
            "type": channel.type.value,
            "guild_id": str(channel.guild.id),
        }

    async def start(self) -> None:
        """Start the Gateway connection."""
        try:
            logger.info("Starting Discord Gateway connection...")
            # Start the client in the background
            asyncio.create_task(self.client.start(self.token))

            # Wait for ready state
            while not self.client.is_ready():
                await asyncio.sleep(0.1)

            logger.info("Gateway connection established")
        except Exception as e:
            logger.error(f"Failed to start Gateway: {e}")
            raise

    async def stop(self) -> None:
        """Stop the Gateway connection."""
        try:
            logger.info("Stopping Discord Gateway connection...")
            await self.client.close()
            self.is_running = False
            logger.info("Gateway connection closed")
        except Exception as e:
            logger.error(f"Error stopping Gateway: {e}")

    def set_event_filters(
        self,
        event_types: Optional[List[str]] = None,
        guild_ids: Optional[List[str]] = None,
        channel_ids: Optional[List[str]] = None,
    ) -> None:
        """Configure event filtering."""
        if event_types is not None:
            self.event_filter.set_event_types(event_types)
        if guild_ids is not None:
            self.event_filter.set_guild_ids(guild_ids)
        if channel_ids is not None:
            self.event_filter.set_channel_ids(channel_ids)

    def clear_event_filters(self) -> None:
        """Clear all event filters."""
        self.event_filter.clear_filters()

    def get_events(
        self, limit: int = 10, since: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """Get buffered events."""
        return self.event_buffer.get_events(limit=limit, since=since)

    def get_gateway_info(self) -> Dict[str, Any]:
        """Get Gateway connection information."""
        return {
            "connected": self.is_running and self.client.is_ready(),
            "user": {
                "id": str(self.client.user.id) if self.client.user else None,
                "username": self.client.user.name if self.client.user else None,
            }
            if self.client.user
            else None,
            "guilds": len(self.client.guilds) if self.client.guilds else 0,
            "latency": round(self.client.latency * 1000, 2),  # Convert to ms
            "intents": self.intents.value,
            "shard_id": getattr(self.client, "shard_id", 0),
            "event_buffer": self.event_buffer.get_stats(),
            "event_filter": self.event_filter.get_filter_status(),
        }
