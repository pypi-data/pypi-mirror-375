"""Auto moderation tools for Discord-Py-Suite using HTTP API."""

import asyncio
from typing import Any, Dict, List, Optional, Union
import json

import aiohttp
from loguru import logger

from ..config import Config


def register_auto_moderation_tools(app, discord_client, config: Config) -> None:
    """Register auto moderation tools with FastMCP."""

    @app.tool()
    async def list_auto_moderation_rules(guild_id: str) -> Dict[str, Any]:
        """List all auto moderation rules for a guild.

        Args:
            guild_id: The ID of the guild to get auto moderation rules from

        Returns:
            Dictionary containing auto moderation rules
        """
        try:
            if not config.discord_token:
                return {"success": False, "error": "Discord token not configured"}

            url = f"https://discord.com/api/v10/guilds/{guild_id}/auto-moderation/rules"
            headers = {
                "Authorization": f"Bot {config.discord_token}",
                "Content-Type": "application/json",
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {"success": True, "data": data}
                    else:
                        error_data = await response.json()
                        return {
                            "success": False,
                            "error": f"Discord API error: {response.status}",
                            "details": error_data,
                        }

        except Exception as e:
            logger.error(f"Error listing auto moderation rules: {e}")
            return {"success": False, "error": str(e)}

    @app.tool()
    async def get_auto_moderation_rule(guild_id: str, rule_id: str) -> Dict[str, Any]:
        """Get a specific auto moderation rule.

        Args:
            guild_id: The ID of the guild
            rule_id: The ID of the auto moderation rule

        Returns:
            Dictionary containing the auto moderation rule
        """
        try:
            if not config.discord_token:
                return {"success": False, "error": "Discord token not configured"}

            url = f"https://discord.com/api/v10/guilds/{guild_id}/auto-moderation/rules/{rule_id}"
            headers = {
                "Authorization": f"Bot {config.discord_token}",
                "Content-Type": "application/json",
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {"success": True, "data": data}
                    else:
                        error_data = await response.json()
                        return {
                            "success": False,
                            "error": f"Discord API error: {response.status}",
                            "details": error_data,
                        }

        except Exception as e:
            logger.error(f"Error getting auto moderation rule: {e}")
            return {"success": False, "error": str(e)}

    @app.tool()
    async def create_auto_moderation_rule(
        guild_id: str,
        name: str,
        event_type: int,
        trigger_type: int,
        trigger_metadata: Dict[str, Any],
        actions: List[Dict[str, Any]],
        enabled: Optional[bool] = True,
        exempt_roles: Optional[List[str]] = None,
        exempt_channels: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Create a new auto moderation rule.

        Args:
            guild_id: The ID of the guild
            name: The name of the rule
            event_type: The event type (1 for MESSAGE_SEND)
            trigger_type: The trigger type (1-5)
            trigger_metadata: Metadata for the trigger
            actions: List of actions to take when triggered
            enabled: Whether the rule is enabled (default True)
            exempt_roles: List of role IDs exempt from this rule
            exempt_channels: List of channel IDs exempt from this rule

        Returns:
            Dictionary containing the created auto moderation rule
        """
        try:
            if not config.discord_token:
                return {"success": False, "error": "Discord token not configured"}

            url = f"https://discord.com/api/v10/guilds/{guild_id}/auto-moderation/rules"
            headers = {
                "Authorization": f"Bot {config.discord_token}",
                "Content-Type": "application/json",
            }

            payload = {
                "name": name,
                "event_type": event_type,
                "trigger_type": trigger_type,
                "trigger_metadata": trigger_metadata,
                "actions": actions,
                "enabled": enabled,
            }

            if exempt_roles:
                payload["exempt_roles"] = exempt_roles
            if exempt_channels:
                payload["exempt_channels"] = exempt_channels

            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {"success": True, "data": data}
                    else:
                        error_data = await response.json()
                        return {
                            "success": False,
                            "error": f"Discord API error: {response.status}",
                            "details": error_data,
                        }

        except Exception as e:
            logger.error(f"Error creating auto moderation rule: {e}")
            return {"success": False, "error": str(e)}

    @app.tool()
    async def modify_auto_moderation_rule(
        guild_id: str,
        rule_id: str,
        name: Optional[str] = None,
        event_type: Optional[int] = None,
        trigger_type: Optional[int] = None,
        trigger_metadata: Optional[Dict[str, Any]] = None,
        actions: Optional[List[Dict[str, Any]]] = None,
        enabled: Optional[bool] = None,
        exempt_roles: Optional[List[str]] = None,
        exempt_channels: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Modify an existing auto moderation rule.

        Args:
            guild_id: The ID of the guild
            rule_id: The ID of the auto moderation rule to modify
            name: The new name of the rule
            event_type: The new event type
            trigger_type: The new trigger type
            trigger_metadata: New metadata for the trigger
            actions: New list of actions
            enabled: Whether the rule should be enabled
            exempt_roles: New list of role IDs exempt from this rule
            exempt_channels: New list of channel IDs exempt from this rule

        Returns:
            Dictionary containing the modified auto moderation rule
        """
        try:
            if not config.discord_token:
                return {"success": False, "error": "Discord token not configured"}

            url = f"https://discord.com/api/v10/guilds/{guild_id}/auto-moderation/rules/{rule_id}"
            headers = {
                "Authorization": f"Bot {config.discord_token}",
                "Content-Type": "application/json",
            }

            payload = {}
            if name is not None:
                payload["name"] = name
            if event_type is not None:
                payload["event_type"] = event_type
            if trigger_type is not None:
                payload["trigger_type"] = trigger_type
            if trigger_metadata is not None:
                payload["trigger_metadata"] = trigger_metadata
            if actions is not None:
                payload["actions"] = actions
            if enabled is not None:
                payload["enabled"] = enabled
            if exempt_roles is not None:
                payload["exempt_roles"] = exempt_roles
            if exempt_channels is not None:
                payload["exempt_channels"] = exempt_channels

            async with aiohttp.ClientSession() as session:
                async with session.patch(
                    url, headers=headers, json=payload
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {"success": True, "data": data}
                    else:
                        error_data = await response.json()
                        return {
                            "success": False,
                            "error": f"Discord API error: {response.status}",
                            "details": error_data,
                        }

        except Exception as e:
            logger.error(f"Error modifying auto moderation rule: {e}")
            return {"success": False, "error": str(e)}

    @app.tool()
    async def delete_auto_moderation_rule(
        guild_id: str, rule_id: str
    ) -> Dict[str, Any]:
        """Delete an auto moderation rule.

        Args:
            guild_id: The ID of the guild
            rule_id: The ID of the auto moderation rule to delete

        Returns:
            Dictionary indicating success or failure
        """
        try:
            if not config.discord_token:
                return {"success": False, "error": "Discord token not configured"}

            url = f"https://discord.com/api/v10/guilds/{guild_id}/auto-moderation/rules/{rule_id}"
            headers = {
                "Authorization": f"Bot {config.discord_token}",
                "Content-Type": "application/json",
            }

            async with aiohttp.ClientSession() as session:
                async with session.delete(url, headers=headers) as response:
                    if response.status == 204:
                        return {
                            "success": True,
                            "message": "Auto moderation rule deleted successfully",
                        }
                    else:
                        error_data = await response.json()
                        return {
                            "success": False,
                            "error": f"Discord API error: {response.status}",
                            "details": error_data,
                        }

        except Exception as e:
            logger.error(f"Error deleting auto moderation rule: {e}")
            return {"success": False, "error": str(e)}

    logger.info("Auto moderation tools registered with FastMCP")
