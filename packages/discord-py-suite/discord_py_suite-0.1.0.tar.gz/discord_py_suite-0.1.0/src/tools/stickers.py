"""Discord stickers FastMCP tools."""

from typing import Any, Dict, Optional, List
import discord
from loguru import logger
import aiohttp
import base64
import os

try:
    from fastmcp import FastMCP
except ImportError:
    logger.error("FastMCP not installed. Please run: uv add fastmcp>=2.12.0")
    raise


def register_stickers_tools(app: FastMCP, client: discord.Client, config: Any) -> None:
    """Register Discord stickers tools with FastMCP app."""

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
        """Check if bot has required permissions for sticker operations."""
        if not client.user:
            return {"success": False, "error": "Client user not available"}

        bot_member = guild.get_member(client.user.id)
        if not bot_member:
            return {"success": False, "error": "Bot is not a member of this guild"}

        # Check for manage_emojis_and_stickers permission
        if not bot_member.guild_permissions.manage_emojis_and_stickers:
            return {
                "success": False,
                "error": "Bot lacks manage_emojis_and_stickers permission",
            }

        return {"success": True}

    @app.tool()
    async def discord_list_guild_stickers(guild_id: str) -> Dict[str, Any]:
        """List stickers in a guild.

        Args:
            guild_id: The guild ID
        """
        try:
            guild = client.get_guild(int(guild_id))
            if not guild:
                return {
                    "success": False,
                    "error": f"Guild {guild_id} not found or bot not in guild",
                }

            # Check basic permissions
            if not client.user:
                return {"success": False, "error": "Client user not available"}

            bot_member = guild.get_member(client.user.id)
            if not bot_member or not bot_member.guild_permissions.view_channel:
                return {"success": False, "error": "Bot lacks view_channel permission"}

            # Get bot token
            token = await _get_bot_token()
            if not token:
                return {"success": False, "error": "Unable to get bot token"}

            # Make API request
            headers = {"Authorization": f"Bot {token}"}

            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"https://discord.com/api/v10/guilds/{guild_id}/stickers",
                    headers=headers,
                ) as response:
                    if response.status == 200:
                        stickers_data = await response.json()
                        stickers = []

                        for sticker in stickers_data:
                            sticker_info = {
                                "id": sticker["id"],
                                "name": sticker["name"],
                                "description": sticker.get("description"),
                                "tags": sticker["tags"],
                                "type": sticker["type"],
                                "format_type": sticker["format_type"],
                                "available": sticker.get("available", True),
                                "guild_id": sticker.get("guild_id"),
                                "user": sticker.get("user"),
                                "sort_value": sticker.get("sort_value"),
                            }
                            stickers.append(sticker_info)

                        return {
                            "success": True,
                            "data": {
                                "guild_id": guild_id,
                                "stickers": stickers,
                                "total_count": len(stickers),
                            },
                        }
                    else:
                        error_text = await response.text()
                        return {
                            "success": False,
                            "error": f"Failed to list guild stickers: {response.status} - {error_text}",
                        }

        except ValueError:
            return {"success": False, "error": "Invalid guild ID format"}
        except Exception as e:
            logger.error(f"Error listing guild stickers: {e}")
            return {"success": False, "error": f"Unexpected error: {e}"}

    @app.tool()
    async def discord_create_guild_sticker(
        guild_id: str,
        name: str,
        tags: str,
        file_path_or_base64: str,
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a guild sticker.

        Args:
            guild_id: The guild ID
            name: Sticker name (max 30 characters)
            tags: Sticker tags (comma-separated)
            file_path_or_base64: Path to sticker file or base64-encoded file data
            description: Sticker description (max 100 characters)
        """
        try:
            guild = client.get_guild(int(guild_id))
            if not guild:
                return {
                    "success": False,
                    "error": f"Guild {guild_id} not found or bot not in guild",
                }

            # Check permissions
            perm_check = await _check_permissions(guild, client)
            if not perm_check["success"]:
                return perm_check

            # Validate inputs
            if len(name) > 30:
                return {
                    "success": False,
                    "error": "Sticker name must be 30 characters or less",
                }

            if description and len(description) > 100:
                return {
                    "success": False,
                    "error": "Description must be 100 characters or less",
                }

            # Handle file input
            file_data = None
            filename = "sticker.png"  # Default filename

            if file_path_or_base64.startswith(("http://", "https://")):
                # URL provided - we would need to download it first
                return {
                    "success": False,
                    "error": "URL file upload not implemented. Please provide a local file path or base64 data.",
                }
            elif os.path.isfile(file_path_or_base64):
                # Local file
                try:
                    with open(file_path_or_base64, "rb") as f:
                        file_data = f.read()

                    # Check file size (512KB limit)
                    if len(file_data) > 512 * 1024:
                        return {
                            "success": False,
                            "error": "Sticker file must be 512KB or smaller",
                        }

                    filename = os.path.basename(file_path_or_base64)
                except Exception as e:
                    return {
                        "success": False,
                        "error": f"Error reading sticker file: {e}",
                    }
            else:
                # Assume base64 data
                try:
                    file_data = base64.b64decode(file_path_or_base64)
                    if len(file_data) > 512 * 1024:
                        return {
                            "success": False,
                            "error": "Sticker file must be 512KB or smaller",
                        }
                except Exception as e:
                    return {"success": False, "error": f"Invalid base64 data: {e}"}

            # Get bot token
            token = await _get_bot_token()
            if not token:
                return {"success": False, "error": "Unable to get bot token"}

            # Prepare form data
            form_data = aiohttp.FormData()

            # Add sticker file
            form_data.add_field(
                "file",
                file_data,
                filename=filename,
                content_type="image/png",  # Assume PNG, Discord will validate
            )

            # Add metadata
            form_data.add_field("name", name)
            form_data.add_field("tags", tags)
            if description:
                form_data.add_field("description", description)

            # Make API request
            headers = {"Authorization": f"Bot {token}"}

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"https://discord.com/api/v10/guilds/{guild_id}/stickers",
                    data=form_data,
                    headers=headers,
                ) as response:
                    if response.status == 201:
                        result = await response.json()
                        return {
                            "success": True,
                            "data": {
                                "sticker_id": result["id"],
                                "name": result["name"],
                                "description": result.get("description"),
                                "tags": result["tags"],
                                "type": result["type"],
                                "format_type": result["format_type"],
                                "available": result.get("available", True),
                                "guild_id": result["guild_id"],
                                "sort_value": result.get("sort_value"),
                            },
                        }
                    else:
                        error_text = await response.text()
                        return {
                            "success": False,
                            "error": f"Failed to create guild sticker: {response.status} - {error_text}",
                        }

        except ValueError:
            return {"success": False, "error": "Invalid guild ID format"}
        except Exception as e:
            logger.error(f"Error creating guild sticker: {e}")
            return {"success": False, "error": f"Unexpected error: {e}"}

    @app.tool()
    async def discord_delete_guild_sticker(
        guild_id: str, sticker_id: str
    ) -> Dict[str, Any]:
        """Delete a guild sticker.

        Args:
            guild_id: The guild ID
            sticker_id: The sticker ID to delete
        """
        try:
            guild = client.get_guild(int(guild_id))
            if not guild:
                return {
                    "success": False,
                    "error": f"Guild {guild_id} not found or bot not in guild",
                }

            # Check permissions
            perm_check = await _check_permissions(guild, client)
            if not perm_check["success"]:
                return perm_check

            # Get bot token
            token = await _get_bot_token()
            if not token:
                return {"success": False, "error": "Unable to get bot token"}

            # Make API request
            headers = {"Authorization": f"Bot {token}"}

            async with aiohttp.ClientSession() as session:
                async with session.delete(
                    f"https://discord.com/api/v10/guilds/{guild_id}/stickers/{sticker_id}",
                    headers=headers,
                ) as response:
                    if response.status == 204:
                        return {
                            "success": True,
                            "data": {
                                "deleted_sticker_id": sticker_id,
                                "guild_id": guild_id,
                            },
                        }
                    else:
                        error_text = await response.text()
                        return {
                            "success": False,
                            "error": f"Failed to delete guild sticker: {response.status} - {error_text}",
                        }

        except ValueError:
            return {"success": False, "error": "Invalid guild ID or sticker ID format"}
        except Exception as e:
            logger.error(f"Error deleting guild sticker: {e}")
            return {"success": False, "error": f"Unexpected error: {e}"}

    @app.tool()
    async def discord_modify_guild_sticker(
        guild_id: str,
        sticker_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Modify a guild sticker.

        Args:
            guild_id: The guild ID
            sticker_id: The sticker ID to modify
            name: New sticker name (max 30 characters)
            description: New description (max 100 characters)
            tags: New tags
        """
        try:
            guild = client.get_guild(int(guild_id))
            if not guild:
                return {
                    "success": False,
                    "error": f"Guild {guild_id} not found or bot not in guild",
                }

            # Check permissions
            perm_check = await _check_permissions(guild, client)
            if not perm_check["success"]:
                return perm_check

            # Validate inputs
            if name and len(name) > 30:
                return {
                    "success": False,
                    "error": "Sticker name must be 30 characters or less",
                }

            if description and len(description) > 100:
                return {
                    "success": False,
                    "error": "Description must be 100 characters or less",
                }

            # Get bot token
            token = await _get_bot_token()
            if not token:
                return {"success": False, "error": "Unable to get bot token"}

            # Prepare update data
            update_data: Dict[str, Any] = {}
            if name is not None:
                update_data["name"] = name
            if description is not None:
                update_data["description"] = description
            if tags is not None:
                update_data["tags"] = tags

            if not update_data:
                return {"success": False, "error": "No fields to update"}

            # Make API request
            headers = {
                "Authorization": f"Bot {token}",
                "Content-Type": "application/json",
            }

            async with aiohttp.ClientSession() as session:
                async with session.patch(
                    f"https://discord.com/api/v10/guilds/{guild_id}/stickers/{sticker_id}",
                    json=update_data,
                    headers=headers,
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "success": True,
                            "data": {
                                "sticker_id": result["id"],
                                "name": result["name"],
                                "description": result.get("description"),
                                "tags": result["tags"],
                                "type": result["type"],
                                "format_type": result["format_type"],
                                "available": result.get("available", True),
                                "guild_id": result["guild_id"],
                                "sort_value": result.get("sort_value"),
                            },
                        }
                    else:
                        error_text = await response.text()
                        return {
                            "success": False,
                            "error": f"Failed to modify guild sticker: {response.status} - {error_text}",
                        }

        except ValueError:
            return {"success": False, "error": "Invalid guild ID or sticker ID format"}
        except Exception as e:
            logger.error(f"Error modifying guild sticker: {e}")
            return {"success": False, "error": f"Unexpected error: {e}"}

    # Log stickers tool registration
    logger.info(
        "Registered Discord stickers tools: list_guild_stickers, create_guild_sticker, delete_guild_sticker, modify_guild_sticker"
    )
