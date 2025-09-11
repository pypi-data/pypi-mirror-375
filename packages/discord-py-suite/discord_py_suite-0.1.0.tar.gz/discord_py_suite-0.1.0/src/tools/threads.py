"""Thread management tools for Discord-Py-Suite using HTTP API."""

import asyncio
from typing import Any, Dict, List, Optional, Union
import json

import aiohttp
from loguru import logger

from ..config import Config


def register_thread_tools(app, discord_client, config: Config) -> None:
    """Register thread management tools with FastMCP."""

    @app.tool()
    async def list_public_archived_threads(
        channel_id: str, before: Optional[str] = None, limit: Optional[int] = 100
    ) -> Dict[str, Any]:
        """List public archived threads in a channel.

        Args:
            channel_id: The ID of the channel to get threads from
            before: Get threads before this thread ID (for pagination)
            limit: Maximum number of threads to return (1-100, default 100)

        Returns:
            Dictionary containing thread information
        """
        try:
            if not config.discord_token:
                return {"success": False, "error": "Discord token not configured"}

            url = f"https://discord.com/api/v10/channels/{channel_id}/threads/archived/public"
            headers = {
                "Authorization": f"Bot {config.discord_token}",
                "Content-Type": "application/json",
            }

            params = {}
            if before:
                params["before"] = before
            if limit and 1 <= limit <= 100:
                params["limit"] = limit

            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "success": True,
                            "data": {
                                "threads": data.get("threads", []),
                                "members": data.get("members", []),
                                "has_more": data.get("has_more", False),
                            },
                        }
                    else:
                        error_data = await response.json()
                        return {
                            "success": False,
                            "error": f"Discord API error: {response.status}",
                            "details": error_data,
                        }

        except Exception as e:
            logger.error(f"Error listing public archived threads: {e}")
            return {"success": False, "error": str(e)}

    @app.tool()
    async def list_private_archived_threads(
        channel_id: str, before: Optional[str] = None, limit: Optional[int] = 100
    ) -> Dict[str, Any]:
        """List private archived threads in a channel.

        Args:
            channel_id: The ID of the channel to get threads from
            before: Get threads before this thread ID (for pagination)
            limit: Maximum number of threads to return (1-100, default 100)

        Returns:
            Dictionary containing thread information
        """
        try:
            if not config.discord_token:
                return {"success": False, "error": "Discord token not configured"}

            url = f"https://discord.com/api/v10/channels/{channel_id}/threads/archived/private"
            headers = {
                "Authorization": f"Bot {config.discord_token}",
                "Content-Type": "application/json",
            }

            params = {}
            if before:
                params["before"] = before
            if limit and 1 <= limit <= 100:
                params["limit"] = limit

            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "success": True,
                            "data": {
                                "threads": data.get("threads", []),
                                "members": data.get("members", []),
                                "has_more": data.get("has_more", False),
                            },
                        }
                    else:
                        error_data = await response.json()
                        return {
                            "success": False,
                            "error": f"Discord API error: {response.status}",
                            "details": error_data,
                        }

        except Exception as e:
            logger.error(f"Error listing private archived threads: {e}")
            return {"success": False, "error": str(e)}

    @app.tool()
    async def list_joined_private_archived_threads(
        channel_id: str, before: Optional[str] = None, limit: Optional[int] = 100
    ) -> Dict[str, Any]:
        """List joined private archived threads in a channel.

        Args:
            channel_id: The ID of the channel to get threads from
            before: Get threads before this thread ID (for pagination)
            limit: Maximum number of threads to return (1-100, default 100)

        Returns:
            Dictionary containing thread information
        """
        try:
            if not config.discord_token:
                return {"success": False, "error": "Discord token not configured"}

            url = f"https://discord.com/api/v10/channels/{channel_id}/users/@me/threads/archived/private"
            headers = {
                "Authorization": f"Bot {config.discord_token}",
                "Content-Type": "application/json",
            }

            params = {}
            if before:
                params["before"] = before
            if limit and 1 <= limit <= 100:
                params["limit"] = limit

            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "success": True,
                            "data": {
                                "threads": data.get("threads", []),
                                "members": data.get("members", []),
                                "has_more": data.get("has_more", False),
                            },
                        }
                    else:
                        error_data = await response.json()
                        return {
                            "success": False,
                            "error": f"Discord API error: {response.status}",
                            "details": error_data,
                        }

        except Exception as e:
            logger.error(f"Error listing joined private archived threads: {e}")
            return {"success": False, "error": str(e)}

    logger.info("Thread management tools registered with FastMCP")
