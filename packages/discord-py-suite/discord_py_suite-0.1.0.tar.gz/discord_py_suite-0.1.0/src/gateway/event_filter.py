"""Event filtering for Discord gateway events."""

from typing import Any, Dict, List, Set


class EventFilter:
    """Filter Discord gateway events based on type, guild, and channel."""

    def __init__(self) -> None:
        self.allowed_event_types: Set[str] = set()
        self.allowed_guild_ids: Set[str] = set()
        self.allowed_channel_ids: Set[str] = set()
        self.filter_active = False

    def set_event_types(self, event_types: List[str]) -> None:
        """Set which event types to include."""
        self.allowed_event_types = set(event_types)
        self._update_filter_status()

    def set_guild_ids(self, guild_ids: List[str]) -> None:
        """Set which guild IDs to include."""
        self.allowed_guild_ids = set(str(gid) for gid in guild_ids)
        self._update_filter_status()

    def set_channel_ids(self, channel_ids: List[str]) -> None:
        """Set which channel IDs to include."""
        self.allowed_channel_ids = set(str(cid) for cid in channel_ids)
        self._update_filter_status()

    def clear_filters(self) -> None:
        """Clear all filters (allow all events)."""
        self.allowed_event_types.clear()
        self.allowed_guild_ids.clear()
        self.allowed_channel_ids.clear()
        self.filter_active = False

    def should_include(self, event: Dict[str, Any]) -> bool:
        """Check if an event should be included based on current filters."""
        if not self.filter_active:
            return True  # No filters, include all events

        # Check event type filter
        if self.allowed_event_types:
            event_type = event.get("type")
            if event_type not in self.allowed_event_types:
                return False

        # Check guild filter
        if self.allowed_guild_ids:
            guild_id = self._extract_guild_id(event)
            if guild_id and str(guild_id) not in self.allowed_guild_ids:
                return False

        # Check channel filter
        if self.allowed_channel_ids:
            channel_id = self._extract_channel_id(event)
            if channel_id and str(channel_id) not in self.allowed_channel_ids:
                return False

        return True

    def _extract_guild_id(self, event: Dict[str, Any]) -> str:
        """Extract guild ID from event data."""
        data = event.get("data", {})

        # Direct guild_id in data
        if "guild_id" in data:
            return str(data["guild_id"])

        # Guild ID in nested objects
        if "guild" in data and isinstance(data["guild"], dict):
            return str(data["guild"].get("id", ""))

        # Guild ID in channel object
        if "channel" in data and isinstance(data["channel"], dict):
            return str(data["channel"].get("guild_id", ""))

        return ""

    def _extract_channel_id(self, event: Dict[str, Any]) -> str:
        """Extract channel ID from event data."""
        data = event.get("data", {})

        # Direct channel_id in data
        if "channel_id" in data:
            return str(data["channel_id"])

        # Channel ID in nested objects
        if "channel" in data and isinstance(data["channel"], dict):
            return str(data["channel"].get("id", ""))

        return ""

    def _update_filter_status(self) -> None:
        """Update whether any filters are active."""
        self.filter_active = bool(
            self.allowed_event_types
            or self.allowed_guild_ids
            or self.allowed_channel_ids
        )

    def get_filter_status(self) -> Dict[str, Any]:
        """Get current filter configuration."""
        return {
            "active": self.filter_active,
            "event_types": list(self.allowed_event_types),
            "guild_ids": list(self.allowed_guild_ids),
            "channel_ids": list(self.allowed_channel_ids),
            "filter_counts": {
                "event_types": len(self.allowed_event_types),
                "guild_ids": len(self.allowed_guild_ids),
                "channel_ids": len(self.allowed_channel_ids),
            },
        }
