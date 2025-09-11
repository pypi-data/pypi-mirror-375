"""Slash command management tools for Discord-Py-Suite using HTTP API."""

import asyncio
from typing import Any, Dict, List, Optional, Union
import json

import aiohttp
from loguru import logger

from ..config import Config


def register_slash_commands_tools(app, discord_client, config: Config) -> None:
    """Register slash command tools with FastMCP."""

    @app.tool()
    async def list_commands(
        application_id: str,
        guild_id: Optional[str] = None,
        with_localizations: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """List all slash commands for an application.

        Args:
            application_id: The application ID (defaults to bot's application)
            guild_id: The guild ID for guild-specific commands
            with_localizations: Whether to include localizations

        Returns:
            Dictionary containing slash commands
        """
        try:
            if not config.discord_token:
                return {"success": False, "error": "Discord token not configured"}

            # Application ID is required
            app_id = application_id

            if guild_id:
                url = f"https://discord.com/api/v10/applications/{app_id}/guilds/{guild_id}/commands"
            else:
                url = f"https://discord.com/api/v10/applications/{app_id}/commands"

            headers = {
                "Authorization": f"Bot {config.discord_token}",
                "Content-Type": "application/json",
            }

            params = {}
            if with_localizations is not None:
                params["with_localizations"] = str(with_localizations).lower()

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
            logger.error(f"Error listing slash commands: {e}")
            return {"success": False, "error": str(e)}

    logger.info("Slash command tools registered with FastMCP")
