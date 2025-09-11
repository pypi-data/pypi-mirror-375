"""Welcome screen management tools for Discord-Py-Suite using HTTP API."""

import asyncio
from typing import Any, Dict, List, Optional, Union
import json

import aiohttp
from loguru import logger

from ..config import Config


def register_welcome_screen_tools(app, discord_client, config: Config) -> None:
    """Register welcome screen tools with FastMCP."""

    @app.tool()
    async def get_welcome_screen(guild_id: str) -> Dict[str, Any]:
        """Get the welcome screen for a guild.

        Args:
            guild_id: The ID of the guild

        Returns:
            Dictionary containing the welcome screen configuration
        """
        try:
            if not config.discord_token:
                return {"success": False, "error": "Discord token not configured"}

            url = f"https://discord.com/api/v10/guilds/{guild_id}/welcome-screen"
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
            logger.error(f"Error getting welcome screen: {e}")
            return {"success": False, "error": str(e)}

    logger.info("Welcome screen tools registered with FastMCP")
