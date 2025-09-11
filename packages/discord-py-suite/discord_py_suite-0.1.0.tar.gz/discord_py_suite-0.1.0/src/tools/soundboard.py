"""Discord soundboard management FastMCP tools."""

from typing import Any, Dict, Optional, List
import discord
from loguru import logger
import aiohttp
import os

try:
    from fastmcp import FastMCP
except ImportError:
    logger.error("FastMCP not installed. Please run: uv add fastmcp>=2.12.0")
    raise


def register_soundboard_tools(
    app: FastMCP, client: discord.Client, config: Any
) -> None:
    """Register Discord soundboard management tools with FastMCP app."""

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
        """Check if bot has required permissions for soundboard operations."""
        if not client.user:
            return {"success": False, "error": "Client user not available"}

        bot_member = guild.get_member(client.user.id)
        if not bot_member:
            return {"success": False, "error": "Bot is not a member of this guild"}

        if not bot_member.guild_permissions.manage_guild:
            return {"success": False, "error": "Bot lacks manage_guild permission"}

        return {"success": True}

    @app.tool()
    async def discord_create_soundboard_sound(
        guildId: str,
        name: str,
        sound: str,
        volume: Optional[float] = None,
        emojiId: Optional[str] = None,
        emojiName: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Creates a new soundboard sound for the server.

        Args:
            guildId: The guild ID
            name: Name of the soundboard sound (max 32 characters)
            sound: Path to sound file or URL (must be MP3, OGG, or WAV, max 512KB)
            volume: Volume level (0.0 to 1.0, default 1.0)
            emojiId: ID of emoji to associate with the sound
            emojiName: Name of emoji to associate with the sound
        """
        try:
            guild = client.get_guild(int(guildId))
            if not guild:
                return {
                    "success": False,
                    "error": f"Guild {guildId} not found or bot not in guild",
                }

            # Check permissions
            perm_check = await _check_permissions(guild, client)
            if not perm_check["success"]:
                return perm_check

            # Get bot token
            token = await _get_bot_token()
            if not token:
                return {"success": False, "error": "Unable to get bot token"}

            # Validate inputs
            if len(name) > 32:
                return {
                    "success": False,
                    "error": "Sound name must be 32 characters or less",
                }

            if volume is not None and (volume < 0.0 or volume > 1.0):
                return {"success": False, "error": "Volume must be between 0.0 and 1.0"}

            # Prepare sound data
            sound_data: Dict[str, Any] = {"name": name}

            # Handle sound file
            if sound.startswith(("http://", "https://")):
                # URL provided
                sound_data["sound"] = sound
            elif os.path.isfile(sound):
                # Local file - we need to upload it
                try:
                    with open(sound, "rb") as f:
                        file_content = f.read()

                    # Check file size (512KB limit)
                    if len(file_content) > 512 * 1024:
                        return {
                            "success": False,
                            "error": "Sound file must be 512KB or smaller",
                        }

                    # For now, we'll use the file path - Discord API expects a URL
                    # In a real implementation, you'd upload to a CDN first
                    return {
                        "success": False,
                        "error": "Local file upload not implemented. Please provide a URL to the sound file.",
                    }
                except Exception as e:
                    return {"success": False, "error": f"Error reading sound file: {e}"}
            else:
                return {
                    "success": False,
                    "error": "Sound must be a valid file path or URL",
                }

            # Add optional parameters
            if volume is not None:
                sound_data["volume"] = float(volume)
            if emojiId:
                sound_data["emoji_id"] = str(emojiId)
            elif emojiName:
                sound_data["emoji_name"] = str(emojiName)

            # Make API request
            headers = {
                "Authorization": f"Bot {token}",
                "Content-Type": "application/json",
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"https://discord.com/api/v10/guilds/{guildId}/soundboard-sounds",
                    json=sound_data,
                    headers=headers,
                ) as response:
                    if response.status == 201:
                        result = await response.json()
                        return {
                            "success": True,
                            "data": {
                                "sound_id": result["id"],
                                "name": result["name"],
                                "volume": result.get("volume", 1.0),
                                "emoji_id": result.get("emoji_id"),
                                "emoji_name": result.get("emoji_name"),
                                "guild_id": guildId,
                                "available": result.get("available", True),
                            },
                        }
                    else:
                        error_text = await response.text()
                        return {
                            "success": False,
                            "error": f"Failed to create soundboard sound: {response.status} - {error_text}",
                        }

        except ValueError:
            return {"success": False, "error": "Invalid guild ID format"}
        except Exception as e:
            logger.error(f"Error creating soundboard sound: {e}")
            return {"success": False, "error": f"Unexpected error: {e}"}

    @app.tool()
    async def discord_delete_soundboard_sound(
        guildId: str, soundId: str
    ) -> Dict[str, Any]:
        """Deletes a soundboard sound from the server.

        Args:
            guildId: The guild ID
            soundId: The soundboard sound ID to delete
        """
        try:
            guild = client.get_guild(int(guildId))
            if not guild:
                return {
                    "success": False,
                    "error": f"Guild {guildId} not found or bot not in guild",
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
                    f"https://discord.com/api/v10/guilds/{guildId}/soundboard-sounds/{soundId}",
                    headers=headers,
                ) as response:
                    if response.status == 204:
                        return {
                            "success": True,
                            "data": {
                                "deleted_sound_id": soundId,
                                "guild_id": guildId,
                            },
                        }
                    else:
                        error_text = await response.text()
                        return {
                            "success": False,
                            "error": f"Failed to delete soundboard sound: {response.status} - {error_text}",
                        }

        except ValueError:
            return {"success": False, "error": "Invalid guild ID or sound ID format"}
        except Exception as e:
            logger.error(f"Error deleting soundboard sound: {e}")
            return {"success": False, "error": f"Unexpected error: {e}"}

    @app.tool()
    async def discord_list_soundboard_sounds(guildId: str) -> Dict[str, Any]:
        """Lists all soundboard sounds in the server.

        Args:
            guildId: The guild ID
        """
        try:
            guild = client.get_guild(int(guildId))
            if not guild:
                return {
                    "success": False,
                    "error": f"Guild {guildId} not found or bot not in guild",
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
                    f"https://discord.com/api/v10/guilds/{guildId}/soundboard-sounds",
                    headers=headers,
                ) as response:
                    if response.status == 200:
                        sounds_data = await response.json()
                        sounds = []

                        for sound in sounds_data:
                            sound_info = {
                                "id": sound["id"],
                                "name": sound["name"],
                                "volume": sound.get("volume", 1.0),
                                "emoji_id": sound.get("emoji_id"),
                                "emoji_name": sound.get("emoji_name"),
                                "available": sound.get("available", True),
                                "user_id": sound.get("user_id"),
                            }
                            sounds.append(sound_info)

                        return {
                            "success": True,
                            "data": {
                                "guild_id": guildId,
                                "sounds": sounds,
                                "total_count": len(sounds),
                            },
                        }
                    else:
                        error_text = await response.text()
                        return {
                            "success": False,
                            "error": f"Failed to list soundboard sounds: {response.status} - {error_text}",
                        }

        except ValueError:
            return {"success": False, "error": "Invalid guild ID format"}
        except Exception as e:
            logger.error(f"Error listing soundboard sounds: {e}")
            return {"success": False, "error": f"Unexpected error: {e}"}

    # Log soundboard tool registration
    logger.info(
        "Registered Discord soundboard management tools: create_soundboard_sound, delete_soundboard_sound, list_soundboard_sounds"
    )
