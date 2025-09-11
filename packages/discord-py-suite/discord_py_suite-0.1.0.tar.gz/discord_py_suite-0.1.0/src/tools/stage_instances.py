"""Stage instance management tools for Discord-Py-Suite using HTTP API."""

import asyncio
from typing import Any, Dict, List, Optional, Union
import json

import aiohttp
from loguru import logger

from ..config import Config


def register_stage_instances_tools(app, discord_client, config: Config) -> None:
    """Register stage instance tools with FastMCP."""

    @app.tool()
    async def get_stage_instance(channel_id: str) -> Dict[str, Any]:
        """Get the stage instance associated with a stage channel.

        Args:
            channel_id: The ID of the stage channel

        Returns:
            Dictionary containing stage instance information
        """
        try:
            if not config.discord_token:
                return {"success": False, "error": "Discord token not configured"}

            url = f"https://discord.com/api/v10/stage-instances/{channel_id}"
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
            logger.error(f"Error getting stage instance: {e}")
            return {"success": False, "error": str(e)}

    @app.tool()
    async def create_stage_instance(
        channel_id: str,
        topic: Optional[str] = None,
        privacy_level: Optional[int] = None,
        send_start_notification: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """Create a stage instance for a stage channel.

        Args:
            channel_id: The ID of the stage channel
            topic: The topic of the stage instance (1-120 characters)
            privacy_level: The privacy level of the stage instance (1 for public, 2 for guild only)
            send_start_notification: Whether to send a notification when the stage starts

        Returns:
            Dictionary containing the created stage instance
        """
        try:
            if not config.discord_token:
                return {"success": False, "error": "Discord token not configured"}

            url = f"https://discord.com/api/v10/stage-instances"
            headers = {
                "Authorization": f"Bot {config.discord_token}",
                "Content-Type": "application/json",
            }

            payload: Dict[str, Any] = {}
            payload["channel_id"] = channel_id

            if topic:
                payload["topic"] = topic
            if privacy_level:
                payload["privacy_level"] = privacy_level
            if send_start_notification is not None:
                payload["send_start_notification"] = send_start_notification

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
            logger.error(f"Error creating stage instance: {e}")
            return {"success": False, "error": str(e)}

    @app.tool()
    async def delete_stage_instance(channel_id: str) -> Dict[str, Any]:
        """Delete the stage instance associated with a stage channel.

        Args:
            channel_id: The ID of the stage channel

        Returns:
            Dictionary indicating success or failure
        """
        try:
            if not config.discord_token:
                return {"success": False, "error": "Discord token not configured"}

            url = f"https://discord.com/api/v10/stage-instances/{channel_id}"
            headers = {
                "Authorization": f"Bot {config.discord_token}",
                "Content-Type": "application/json",
            }

            async with aiohttp.ClientSession() as session:
                async with session.delete(url, headers=headers) as response:
                    if response.status == 204:
                        return {
                            "success": True,
                            "message": "Stage instance deleted successfully",
                        }
                    else:
                        error_data = await response.json()
                        return {
                            "success": False,
                            "error": f"Discord API error: {response.status}",
                            "details": error_data,
                        }

        except Exception as e:
            logger.error(f"Error deleting stage instance: {e}")
            return {"success": False, "error": str(e)}

    logger.info("Stage instance tools registered with FastMCP")
