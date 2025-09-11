"""Type definitions and helper functions for Discord-Py-Suite."""

from typing import Any, Dict, List, Optional, Union, TYPE_CHECKING
import discord

if TYPE_CHECKING:
    from fastmcp import FastMCP

# Type aliases for better readability
MessageableChannel = Union[
    discord.TextChannel,
    discord.DMChannel,
    discord.GroupChannel,
    discord.Thread,
    discord.VoiceChannel,
    discord.StageChannel,
]

# Safe channel types that support fetch_message
FetchableChannel = Union[
    discord.TextChannel, discord.DMChannel, discord.GroupChannel, discord.Thread
]

# Guild channel types
GuildChannelType = Union[
    discord.TextChannel,
    discord.VoiceChannel,
    discord.CategoryChannel,
    discord.StageChannel,
    discord.ForumChannel,
    discord.Thread,
]


async def safe_channel_fetch_message(
    channel: discord.abc.GuildChannel, message_id: int
) -> Optional[discord.Message]:
    """Safely fetch a message from a channel if it supports it."""
    if isinstance(
        channel,
        (discord.TextChannel, discord.DMChannel, discord.GroupChannel, discord.Thread),
    ):
        return await channel.fetch_message(message_id)
    return None


def safe_get_voice_state_attr(
    voice_state: Optional[discord.VoiceState], attr: str
) -> bool:
    """Safely get voice state attributes with correct names."""
    if not voice_state:
        return False

    # Map common attribute names to correct discord.py names
    attr_map = {
        "muted": "mute",
        "deafened": "deaf",
        "is_muted": "mute",
        "is_deafened": "deaf",
    }

    actual_attr = attr_map.get(attr, attr)
    return getattr(voice_state, actual_attr, False)


def safe_isoformat(dt: Optional[Any]) -> Optional[str]:
    """Safely convert datetime to isoformat string."""
    if dt and hasattr(dt, "isoformat"):
        result = dt.isoformat()
        # Ensure we return str, not Any
        return str(result) if result is not None else None
    return None
