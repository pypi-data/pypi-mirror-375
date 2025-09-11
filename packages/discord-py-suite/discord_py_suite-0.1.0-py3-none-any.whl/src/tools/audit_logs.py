"""Audit logs tools for Discord-Py-Suite using HTTP API."""

import asyncio
from typing import Any, Dict, List, Optional, Union
import json

import aiohttp
from loguru import logger

from ..config import Config


def register_audit_logs_tools(app, discord_client, config: Config) -> None:
    """Register audit logs tools with FastMCP."""

    @app.tool()
    async def get_audit_log(
        guild_id: str,
        user_id: Optional[str] = None,
        action_type: Optional[int] = None,
        before: Optional[str] = None,
        limit: Optional[int] = 50,
    ) -> Dict[str, Any]:
        """Get audit log entries for a guild.

        Args:
            guild_id: The ID of the guild
            user_id: Filter by user ID
            action_type: Filter by action type (1-139)
            before: Get entries before this audit log entry ID
            limit: Maximum number of entries to return (1-100, default 50)

        Returns:
            Dictionary containing audit log entries
        """
        try:
            if not config.discord_token:
                return {"success": False, "error": "Discord token not configured"}

            url = f"https://discord.com/api/v10/guilds/{guild_id}/audit-logs"
            headers = {
                "Authorization": f"Bot {config.discord_token}",
                "Content-Type": "application/json",
            }

            params = {}
            if user_id:
                params["user_id"] = user_id
            if action_type:
                params["action_type"] = action_type
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
                                "audit_log_entries": data.get("audit_log_entries", []),
                                "users": data.get("users", []),
                                "integrations": data.get("integrations", []),
                                "threads": data.get("threads", []),
                                "webhooks": data.get("webhooks", []),
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
            logger.error(f"Error getting audit log: {e}")
            return {"success": False, "error": str(e)}

    logger.info("Audit logs tools registered with FastMCP")
