"""Security policy implementation for Discord-Py-Suite."""

from typing import Any, Dict, List, Set
from ..config import Config


class SecurityPolicy:
    """Security policy enforcement for Discord operations."""

    def __init__(self, config: Config):
        self.config = config
        self.allow_guilds: Set[str] = set(config.allow_guild_ids)
        self.allow_channels: Set[str] = set(config.allow_channel_ids)
        self.default_allowed_mentions = config.default_allowed_mentions

        # Destructive operations requiring confirmation
        self.destructive_tools = {
            "discord_delete_channel",
            "discord_ban_member",
            "discord_ban_user",
            "discord_delete_role",
            "discord_bulk_delete_messages",
            "discord_kick_member",
            "discord_delete_guild",
            "discord_delete_webhook",
            "discord_delete_forum_post",
            "discord_delete_scheduled_event",
            "discord_delete_emoji",
            "discord_delete_sticker",
            "discord_delete_invite",
            "discord_delete_integration",
            "discord_begin_prune",
            "discord_unban_member",
            "discord_timeout_member",
            "discord_delete_command",
            "discord_delete_thread",
        }

        # High privilege operations requiring extra confirmation
        self.high_privilege_tools = {
            "discord_ban_member",
            "discord_ban_user",
            "discord_begin_prune",
            "discord_delete_guild",
            "discord_bulk_delete_messages",
        }

    def validate_guild(self, guild_id: str) -> bool:
        """Check if guild access is allowed."""
        if not self.allow_guilds:
            return True  # No restriction if allowlist is empty
        return guild_id in self.allow_guilds

    def validate_channel(self, channel_id: str) -> bool:
        """Check if channel access is allowed."""
        if not self.allow_channels:
            return True  # No restriction if allowlist is empty
        return channel_id in self.allow_channels

    def validate_access(self, tool_name: str, parameters: Dict[str, Any]) -> None:
        """Validate access permissions for a tool call."""
        # Check guild access
        if "guild_id" in parameters:
            guild_id = str(parameters["guild_id"])
            if not self.validate_guild(guild_id):
                raise PermissionError(
                    f"Guild {guild_id} not allowed by security policy"
                )

        # Check channel access
        if "channel_id" in parameters:
            channel_id = str(parameters["channel_id"])
            if not self.validate_channel(channel_id):
                raise PermissionError(
                    f"Channel {channel_id} not allowed by security policy"
                )

    def requires_confirmation(self, tool_name: str) -> bool:
        """Check if tool requires user confirmation before execution."""
        return tool_name in self.destructive_tools

    def requires_high_privilege_confirmation(self, tool_name: str) -> bool:
        """Check if tool requires extra confirmation due to high privilege level."""
        return tool_name in self.high_privilege_tools

    def get_allowed_mentions(self) -> Dict[str, Any]:
        """Get default allowed mentions configuration."""
        if self.default_allowed_mentions == "none":
            return {"parse": []}
        elif self.default_allowed_mentions == "users":
            return {"parse": ["users"]}
        elif self.default_allowed_mentions == "roles":
            return {"parse": ["roles"]}
        elif self.default_allowed_mentions == "everyone":
            return {"parse": ["users", "roles", "everyone"]}
        else:
            return {"parse": []}  # Safe default

    def sanitize_mentions(self, content: str) -> str:
        """Sanitize mentions in message content based on policy."""
        if self.default_allowed_mentions == "none":
            # Replace @everyone and @here with safe versions
            content = content.replace("@everyone", "@\u200beveryone")
            content = content.replace("@here", "@\u200bhere")
        return content

    def get_security_status(self) -> Dict[str, Any]:
        """Get current security policy status."""
        return {
            "guild_allowlist_enabled": len(self.allow_guilds) > 0,
            "channel_allowlist_enabled": len(self.allow_channels) > 0,
            "allowed_guilds_count": len(self.allow_guilds),
            "allowed_channels_count": len(self.allow_channels),
            "default_mentions_policy": self.default_allowed_mentions,
            "destructive_tools_count": len(self.destructive_tools),
            "high_privilege_tools_count": len(self.high_privilege_tools),
        }
