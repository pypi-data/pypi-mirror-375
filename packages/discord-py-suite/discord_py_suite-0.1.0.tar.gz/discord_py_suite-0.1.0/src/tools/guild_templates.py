"""Guild template management tools for Discord-Py-Suite using HTTP API."""

import asyncio
from typing import Any, Dict, List, Optional, Union
import json

import aiohttp
from loguru import logger

from ..config import Config


def register_guild_templates_tools(app, discord_client, config: Config) -> None:
    """Register guild template tools with FastMCP."""

    @app.tool()
    async def list_guild_templates(guild_id: str) -> Dict[str, Any]:
        """List all templates for a guild.

        Args:
            guild_id: The ID of the guild

        Returns:
            Dictionary containing guild templates
        """
        try:
            if not config.discord_token:
                return {"success": False, "error": "Discord token not configured"}

            url = f"https://discord.com/api/v10/guilds/{guild_id}/templates"
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
            logger.error(f"Error listing guild templates: {e}")
            return {"success": False, "error": str(e)}

    @app.tool()
    async def sync_guild_template(guild_id: str, template_code: str) -> Dict[str, Any]:
        """Sync a guild template.

        Args:
            guild_id: The ID of the guild
            template_code: The template code

        Returns:
            Dictionary containing the synced template
        """
        try:
            if not config.discord_token:
                return {"success": False, "error": "Discord token not configured"}

            url = f"https://discord.com/api/v10/guilds/{guild_id}/templates/{template_code}"
            headers = {
                "Authorization": f"Bot {config.discord_token}",
                "Content-Type": "application/json",
            }

            async with aiohttp.ClientSession() as session:
                async with session.put(url, headers=headers) as response:
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
            logger.error(f"Error syncing guild template: {e}")
            return {"success": False, "error": str(e)}

    logger.info("Guild template tools registered with FastMCP")
