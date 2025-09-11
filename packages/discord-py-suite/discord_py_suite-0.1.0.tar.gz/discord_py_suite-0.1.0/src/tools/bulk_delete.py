"""Discord bulk message deletion FastMCP tools."""

from typing import Any, Dict, Optional, List
import discord
from loguru import logger
import aiohttp

try:
    from fastmcp import FastMCP
except ImportError:
    logger.error("FastMCP not installed. Please run: uv add fastmcp>=2.12.0")
    raise


def register_bulk_delete_tools(
    app: FastMCP, client: discord.Client, config: Any
) -> None:
    """Register Discord bulk message deletion tools with FastMCP app."""

    async def _get_bot_token() -> Optional[str]:
        """Get the bot token from the client."""
        try:
            # Try different ways to get the token
            if hasattr(client, "http") and hasattr(client.http, "token"):
                return client.http.token
            else:
                # Try to get from config
                return getattr(config, "discord_token", None)
        except Exception:
            return None

    async def _check_permissions(
        guild: discord.Guild, client: discord.Client
    ) -> Dict[str, Any]:
        """Check if bot has required permissions for bulk deletion."""
        if not client.user:
            return {"success": False, "error": "Client user not available"}

        bot_member = guild.get_member(client.user.id)
        if not bot_member:
            return {"success": False, "error": "Bot is not a member of this guild"}

        if not bot_member.guild_permissions.manage_messages:
            return {"success": False, "error": "Bot lacks manage_messages permission"}

        return {"success": True}

    @app.tool()
    async def discord_bulk_delete_messages(
        channel_id: str, message_ids: List[str]
    ) -> Dict[str, Any]:
        """Bulk delete 2-100 messages from a channel.

        Args:
            channel_id: The channel ID where messages should be deleted
            message_ids: List of message IDs to delete (2-100 messages)
        """
        try:
            # Validate input
            if len(message_ids) < 2 or len(message_ids) > 100:
                return {
                    "success": False,
                    "error": "Must provide between 2 and 100 message IDs for bulk deletion",
                }

            # Get channel and guild
            channel = client.get_channel(int(channel_id))
            if not channel:
                return {
                    "success": False,
                    "error": f"Channel {channel_id} not found",
                }

            if not isinstance(channel, discord.TextChannel):
                return {
                    "success": False,
                    "error": "Bulk deletion is only supported in text channels",
                }

            # Check permissions
            perm_check = await _check_permissions(channel.guild, client)
            if not perm_check["success"]:
                return perm_check

            # Get bot token
            token = await _get_bot_token()
            if not token:
                return {"success": False, "error": "Unable to get bot token"}

            # Make API request
            headers = {"Authorization": f"Bot {token}"}

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"https://discord.com/api/v10/channels/{channel_id}/messages/bulk-delete",
                    json={"messages": message_ids},
                    headers=headers,
                ) as response:
                    if response.status == 204:
                        return {
                            "success": True,
                            "data": {
                                "channel_id": channel_id,
                                "deleted_count": len(message_ids),
                                "message_ids": message_ids,
                            },
                        }
                    else:
                        error_text = await response.text()
                        return {
                            "success": False,
                            "error": f"Failed to bulk delete messages: {response.status} - {error_text}",
                        }

        except ValueError:
            return {
                "success": False,
                "error": "Invalid channel ID or message ID format",
            }
        except Exception as e:
            logger.error(f"Error bulk deleting messages: {e}")
            return {"success": False, "error": f"Unexpected error: {e}"}

    # Log bulk delete tool registration
    logger.info("Registered Discord bulk message deletion tool: bulk_delete_messages")
