"""Advanced operations tools for Discord-Py-Suite using HTTP API."""

import asyncio
from typing import Any, Dict, List, Optional, Union
import json

import aiohttp
from loguru import logger

from ..config import Config


def register_advanced_operations_tools(app, discord_client, config: Config) -> None:
    """Register advanced operations tools with FastMCP."""

    @app.tool()
    async def crosspost_message(channel_id: str, message_id: str) -> Dict[str, Any]:
        """Crosspost a message to all channels following the announcement channel.

        Args:
            channel_id: The ID of the announcement channel
            message_id: The ID of the message to crosspost

        Returns:
            Dictionary containing the crossposted message
        """
        try:
            if not config.discord_token:
                return {"success": False, "error": "Discord token not configured"}

            url = f"https://discord.com/api/v10/channels/{channel_id}/messages/{message_id}/crosspost"
            headers = {
                "Authorization": f"Bot {config.discord_token}",
                "Content-Type": "application/json",
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers) as response:
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
            logger.error(f"Error crossposting message: {e}")
            return {"success": False, "error": str(e)}

    @app.tool()
    async def get_reactors(
        channel_id: str,
        message_id: str,
        emoji: str,
        after: Optional[str] = None,
        limit: Optional[int] = 25,
    ) -> Dict[str, Any]:
        """Get users who reacted with a specific emoji to a message.

        Args:
            channel_id: The ID of the channel
            message_id: The ID of the message
            emoji: The emoji to get reactions for (unicode or custom emoji)
            after: Get reactions after this user ID
            limit: Maximum number of users to return (1-100, default 25)

        Returns:
            Dictionary containing the list of users who reacted
        """
        try:
            if not config.discord_token:
                return {"success": False, "error": "Discord token not configured"}

            url = f"https://discord.com/api/v10/channels/{channel_id}/messages/{message_id}/reactions/{emoji}"
            headers = {
                "Authorization": f"Bot {config.discord_token}",
                "Content-Type": "application/json",
            }

            params = {}
            if after:
                params["after"] = after
            if limit and 1 <= limit <= 100:
                params["limit"] = limit

            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params) as response:
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
            logger.error(f"Error getting reactors: {e}")
            return {"success": False, "error": str(e)}

    @app.tool()
    async def search_guild_members(
        guild_id: str, query: str, limit: Optional[int] = 1
    ) -> Dict[str, Any]:
        """Search for guild members by username or nickname.

        Args:
            guild_id: The ID of the guild
            query: Search query string
            limit: Maximum number of members to return (1-1000, default 1)

        Returns:
            Dictionary containing the list of matching members
        """
        try:
            if not config.discord_token:
                return {"success": False, "error": "Discord token not configured"}

            url = f"https://discord.com/api/v10/guilds/{guild_id}/members/search"
            headers = {
                "Authorization": f"Bot {config.discord_token}",
                "Content-Type": "application/json",
            }

            params: Dict[str, Any] = {"query": query}
            if limit and 1 <= limit <= 1000:
                params["limit"] = limit

            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params) as response:
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
            logger.error(f"Error searching guild members: {e}")
            return {"success": False, "error": str(e)}

    @app.tool()
    async def modify_guild_member(
        guild_id: str,
        user_id: str,
        nick: Optional[str] = None,
        roles: Optional[List[str]] = None,
        mute: Optional[bool] = None,
        deaf: Optional[bool] = None,
        channel_id: Optional[str] = None,
        communication_disabled_until: Optional[str] = None,
        flags: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Modify a guild member.

        Args:
            guild_id: The ID of the guild
            user_id: The ID of the user
            nick: New nickname for the member
            roles: Array of role IDs for the member
            mute: Whether the member should be muted
            deaf: Whether the member should be deafened
            channel_id: ID of the channel to move the member to
            communication_disabled_until: ISO8601 timestamp for timeout expiration
            flags: Guild member flags

        Returns:
            Dictionary containing the modified member
        """
        try:
            if not config.discord_token:
                return {"success": False, "error": "Discord token not configured"}

            url = f"https://discord.com/api/v10/guilds/{guild_id}/members/{user_id}"
            headers = {
                "Authorization": f"Bot {config.discord_token}",
                "Content-Type": "application/json",
            }

            payload = {}
            if nick is not None:
                payload["nick"] = nick
            if roles is not None:
                payload["roles"] = roles
            if mute is not None:
                payload["mute"] = mute
            if deaf is not None:
                payload["deaf"] = deaf
            if channel_id is not None:
                payload["channel_id"] = channel_id
            if communication_disabled_until is not None:
                payload["communication_disabled_until"] = communication_disabled_until
            if flags is not None:
                payload["flags"] = str(flags)

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
            logger.error(f"Error modifying guild member: {e}")
            return {"success": False, "error": str(e)}

    logger.info("Advanced operations tools registered with FastMCP")
