"""Voice channel management FastMCP tools."""

from typing import Any, Dict, Optional
import discord
from loguru import logger

try:
    from fastmcp import FastMCP
except ImportError:
    logger.error("FastMCP not installed. Please run: uv add fastmcp>=2.12.0")
    raise


def register_voice_tools(app: FastMCP, client: discord.Client, config: Any) -> None:
    """Register voice channel tools with FastMCP app."""

    @app.tool()
    async def discord_move_voice_member(
        user_id: str, channel_id: str, reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """Move a member to a different voice channel.

        Args:
            user_id: The Discord user ID to move
            channel_id: The target voice channel ID
            reason: Optional reason for the action

        Returns:
            Success status with moved member info
        """
        try:
            # Get guild from channel_id
            channel = client.get_channel(int(channel_id))
            if not isinstance(channel, discord.VoiceChannel):
                return {"success": False, "error": "Channel is not a voice channel"}
            guild = channel.guild

            # Permission check
            bot_member = guild.get_member(client.user.id) if client.user else None
            if not bot_member or not bot_member.guild_permissions.move_members:
                return {"success": False, "error": "Bot lacks move_members permission"}

            # Get member
            member = guild.get_member(int(user_id))
            if not member:
                return {
                    "success": False,
                    "error": f"Member {user_id} not found in guild",
                }

            # Move member
            await member.move_to(channel, reason=reason or "Moved by FastMCP tool")

            return {
                "success": True,
                "data": {
                    "user_id": str(member.id),
                    "username": str(member),
                    "channel_id": str(channel.id),
                    "channel_name": channel.name,
                    "reason": reason,
                },
            }
        except discord.Forbidden:
            return {"success": False, "error": "Bot lacks required permissions"}
        except discord.NotFound:
            return {"success": False, "error": "Member or channel not found"}
        except discord.HTTPException as e:
            return {"success": False, "error": f"Discord API error: {e}"}
        except Exception as e:
            logger.error(f"Error in move_voice_member: {e}")
            return {"success": False, "error": str(e)}

    @app.tool()
    async def discord_disconnect_voice_member(
        user_id: str, guild_id: str, reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """Disconnect a member from their current voice channel (kick from voice).

        Args:
            user_id: The Discord user ID to disconnect
            guild_id: The Discord server (guild) ID
            reason: Optional reason for the action

        Returns:
            Success status with disconnected member info
        """
        try:
            guild = client.get_guild(int(guild_id))
            if not guild:
                return {"success": False, "error": f"Guild {guild_id} not found"}

            # Permission check - requires kick_members permission for voice disconnect
            bot_member = guild.get_member(client.user.id) if client.user else None
            if not bot_member or not bot_member.guild_permissions.kick_members:
                return {"success": False, "error": "Bot lacks kick_members permission"}

            member = guild.get_member(int(user_id))
            if not member:
                return {
                    "success": False,
                    "error": f"Member {user_id} not found in guild",
                }

            # Check if member is in voice
            voice_state = member.voice
            if not voice_state or not voice_state.channel:
                return {"success": False, "error": "Member is not in a voice channel"}

            await member.move_to(None, reason=reason or "Disconnected by FastMCP tool")

            return {
                "success": True,
                "data": {
                    "user_id": str(member.id),
                    "username": str(member),
                    "previous_channel": {
                        "id": str(voice_state.channel.id),
                        "name": voice_state.channel.name,
                    },
                    "reason": reason,
                },
            }
        except discord.Forbidden:
            return {"success": False, "error": "Bot lacks required permissions"}
        except discord.NotFound:
            return {"success": False, "error": "Member not found"}
        except discord.HTTPException as e:
            return {"success": False, "error": f"Discord API error: {e}"}
        except Exception as e:
            logger.error(f"Error in disconnect_voice_member: {e}")
            return {"success": False, "error": str(e)}

    @app.tool()
    async def discord_create_voice_channel(
        guild_id: str,
        name: str,
        user_limit: Optional[int] = 0,
        bitrate: Optional[int] = 64000,
    ) -> Dict[str, Any]:
        """Create a new voice channel in the server.

        Args:
            guild_id: The Discord server (guild) ID
            name: The name for the new voice channel
            user_limit: Optional user limit (0 = unlimited)
            bitrate: Optional bitrate in bits per second (default 64000)

        Returns:
            Success status with created channel info
        """
        try:
            guild = client.get_guild(int(guild_id))
            if not guild:
                return {"success": False, "error": f"Guild {guild_id} not found"}

            bot_member = guild.get_member(client.user.id) if client.user else None
            if not bot_member or not bot_member.guild_permissions.manage_channels:
                return {
                    "success": False,
                    "error": "Bot lacks manage_channels permission",
                }

            # Clamp bitrate to Discord limits (8000-384000 bps, or 128000 for VIP)
            max_bitrate = 128000 if guild.premium_tier > 0 else 96000
            bitrate = min(max(8000, bitrate or 64000), max_bitrate)

            user_limit = max(0, min(99, user_limit or 0))  # Discord limits: 0-99

            channel = await guild.create_voice_channel(
                name=name,
                bitrate=bitrate,
                user_limit=user_limit,
                reason="Created by FastMCP tool",
            )

            return {
                "success": True,
                "data": {
                    "id": str(channel.id),
                    "name": channel.name,
                    "guild_id": str(guild.id),
                    "type": "voice",
                    "bitrate": channel.bitrate,
                    "user_limit": channel.user_limit,
                },
            }
        except discord.Forbidden:
            return {"success": False, "error": "Bot lacks required permissions"}
        except discord.HTTPException as e:
            return {"success": False, "error": f"Discord API error: {e}"}
        except Exception as e:
            logger.error(f"Error in create_voice_channel: {e}")
            return {"success": False, "error": str(e)}

    @app.tool()
    async def discord_modify_voice_channel(
        channel_id: str,
        name: Optional[str] = None,
        user_limit: Optional[int] = None,
        bitrate: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Modify an existing voice channel.

        Args:
            channel_id: The voice channel ID to modify
            name: Optional new name
            user_limit: Optional new user limit (0 = unlimited)
            bitrate: Optional new bitrate in bits per second

        Returns:
            Success status with updated channel info
        """
        try:
            channel = client.get_channel(int(channel_id))
            if not isinstance(channel, discord.VoiceChannel):
                return {"success": False, "error": "Channel is not a voice channel"}

            guild = channel.guild
            bot_member = guild.get_member(client.user.id) if client.user else None
            if not bot_member or not bot_member.guild_permissions.manage_channels:
                return {
                    "success": False,
                    "error": "Bot lacks manage_channels permission",
                }

            # Build modification kwargs
            modification_data: Dict[str, Any] = {}
            if name is not None:
                modification_data["name"] = name

            if user_limit is not None:
                user_limit = max(0, min(99, user_limit))
                modification_data["user_limit"] = user_limit

            if bitrate is not None:
                max_bitrate = 128000 if guild.premium_tier > 0 else 96000
                bitrate = min(max(8000, bitrate), max_bitrate)
                modification_data["bitrate"] = bitrate

            if not modification_data:
                return {"success": False, "error": "No valid modifications provided"}

            modification_data["reason"] = "Modified by FastMCP tool"
            await channel.edit(**modification_data)

            return {
                "success": True,
                "data": {
                    "id": str(channel.id),
                    "name": channel.name,
                    "guild_id": str(guild.id),
                    "bitrate": channel.bitrate,
                    "user_limit": channel.user_limit,
                },
            }
        except discord.Forbidden:
            return {"success": False, "error": "Bot lacks required permissions"}
        except discord.NotFound:
            return {"success": False, "error": "Channel not found"}
        except discord.HTTPException as e:
            return {"success": False, "error": f"Discord API error: {e}"}
        except Exception as e:
            logger.error(f"Error in modify_voice_channel: {e}")
            return {"success": False, "error": str(e)}

    @app.tool()
    async def discord_get_voice_channel_members(channel_id: str) -> Dict[str, Any]:
        """Get list of members currently in a voice channel.

        Args:
            channel_id: The voice channel ID to check

        Returns:
            Success status with list of members in the channel
        """
        try:
            channel = client.get_channel(int(channel_id))
            if not isinstance(channel, discord.VoiceChannel):
                return {"success": False, "error": "Channel is not a voice channel"}

            # Check if bot can access the channel
            bot_member = (
                channel.guild.get_member(client.user.id) if client.user else None
            )
            bot_voice_state = bot_member.voice if bot_member else None
            has_access = (
                bot_voice_state
                and bot_voice_state.channel == channel
                or channel.guild.voice_channels
            )

            members = []
            for member in channel.members:
                members.append(
                    {
                        "id": str(member.id),
                        "username": member.name,
                        "display_name": member.display_name,
                        "discriminator": member.discriminator,
                        "nick": member.nick,
                        "avatar": member.avatar.url if member.avatar else None,
                        "joined_at": member.joined_at.isoformat()
                        if member.joined_at
                        else None,
                        "is_muted": member.voice.mute if member.voice else False,
                        "is_deafened": member.voice.deaf if member.voice else False,
                        "is_streaming": member.voice.self_stream
                        if member.voice
                        else False,
                        "is_video": member.voice.self_video if member.voice else False,
                    }
                )

            return {
                "success": True,
                "data": {
                    "channel": {
                        "id": str(channel.id),
                        "name": channel.name,
                        "guild_id": str(channel.guild.id),
                        "member_count": len(members),
                    },
                    "members": members,
                },
            }
        except discord.Forbidden:
            return {"success": False, "error": "Bot lacks required permissions"}
        except discord.NotFound:
            return {"success": False, "error": "Channel not found"}
        except discord.HTTPException as e:
            return {"success": False, "error": f"Discord API error: {e}"}
        except Exception as e:
            logger.error(f"Error in get_voice_channel_members: {e}")
            return {"success": False, "error": str(e)}

    @app.tool()
    async def discord_create_voice_channel_from_template(
        guild_id: str, template: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a voice channel from a template configuration.

        Args:
            guild_id: The Discord server (guild) ID
            template: Dictionary containing channel template configuration

        Returns:
            Success status with created channel info
        """
        # Extract template parameters with defaults
        name = template.get("name", "Voice Channel")
        user_limit = template.get("user_limit", 0)
        bitrate = template.get("bitrate", 64000)
        category_id = template.get("category_id")

        try:
            guild = client.get_guild(int(guild_id))
            if not guild:
                return {"success": False, "error": f"Guild {guild_id} not found"}

            bot_member = guild.get_member(client.user.id) if client.user else None
            if not bot_member or not bot_member.guild_permissions.manage_channels:
                return {
                    "success": False,
                    "error": "Bot lacks manage_channels permission",
                }

            # Handle category positioning
            category: Optional[discord.CategoryChannel] = None
            if category_id:
                potential_category = guild.get_channel(int(category_id))
                if isinstance(potential_category, discord.CategoryChannel):
                    category = potential_category

            # Clamp bitrate to Discord limits (8000-384000 bps, or 128000 for VIP)
            max_bitrate = 128000 if guild.premium_tier > 0 else 96000
            bitrate = min(max(8000, bitrate), max_bitrate)

            user_limit = max(0, min(99, user_limit))  # Discord limits: 0-99

            channel = await guild.create_voice_channel(
                name=name,
                bitrate=bitrate,
                user_limit=user_limit,
                category=category,
                reason="Created from template by FastMCP tool",
            )

            return {
                "success": True,
                "data": {
                    "id": str(channel.id),
                    "name": channel.name,
                    "guild_id": str(guild.id),
                    "category_id": str(category.id) if category else None,
                    "category_name": category.name if category else None,
                    "bitrate": channel.bitrate,
                    "user_limit": channel.user_limit,
                },
            }
        except discord.Forbidden:
            return {"success": False, "error": "Bot lacks required permissions"}
        except discord.NotFound:
            return {"success": False, "error": "Guild or category not found"}
        except discord.HTTPException as e:
            return {"success": False, "error": f"Discord API error: {e}"}
        except Exception as e:
            logger.error(f"Error in create_voice_channel_from_template: {e}")
            return {"success": False, "error": str(e)}

    @app.tool()
    async def discord_mute_voice_member(
        user_id: str, guild_id: str, reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """Server mute a member in voice channels.

        Args:
            user_id: The Discord user ID to mute
            guild_id: The Discord server (guild) ID
            reason: Optional reason for the action

        Returns:
            Success status with muted member info
        """
        try:
            guild = client.get_guild(int(guild_id))
            if not guild:
                return {"success": False, "error": f"Guild {guild_id} not found"}

            bot_member = guild.get_member(client.user.id) if client.user else None
            if not bot_member or not bot_member.guild_permissions.mute_members:
                return {"success": False, "error": "Bot lacks mute_members permission"}

            member = guild.get_member(int(user_id))
            if not member:
                return {
                    "success": False,
                    "error": f"Member {user_id} not found in guild",
                }

            await member.edit(mute=True, reason=reason or "Muted by FastMCP tool")

            return {
                "success": True,
                "data": {
                    "user_id": str(member.id),
                    "username": str(member),
                    "action": "muted",
                    "reason": reason,
                },
            }
        except discord.Forbidden:
            return {"success": False, "error": "Bot lacks required permissions"}
        except discord.NotFound:
            return {"success": False, "error": "Member not found"}
        except discord.HTTPException as e:
            return {"success": False, "error": f"Discord API error: {e}"}
        except Exception as e:
            logger.error(f"Error in mute_voice_member: {e}")
            return {"success": False, "error": str(e)}

    @app.tool()
    async def discord_deafen_voice_member(
        user_id: str, guild_id: str, reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """Server deafen a member in voice channels.

        Args:
            user_id: The Discord user ID to deafen
            guild_id: The Discord server (guild) ID
            reason: Optional reason for the action

        Returns:
            Success status with deafened member info
        """
        try:
            guild = client.get_guild(int(guild_id))
            if not guild:
                return {"success": False, "error": f"Guild {guild_id} not found"}

            bot_member = guild.get_member(client.user.id) if client.user else None
            if not bot_member or not bot_member.guild_permissions.deafen_members:
                return {
                    "success": False,
                    "error": "Bot lacks deafen_members permission",
                }

            member = guild.get_member(int(user_id))
            if not member:
                return {
                    "success": False,
                    "error": f"Member {user_id} not found in guild",
                }

            await member.edit(deafen=True, reason=reason or "Deafened by FastMCP tool")

            return {
                "success": True,
                "data": {
                    "user_id": str(member.id),
                    "username": str(member),
                    "action": "deafened",
                    "reason": reason,
                },
            }
        except discord.Forbidden:
            return {"success": False, "error": "Bot lacks required permissions"}
        except discord.NotFound:
            return {"success": False, "error": "Member not found"}
        except discord.HTTPException as e:
            return {"success": False, "error": f"Discord API error: {e}"}
        except Exception as e:
            logger.error(f"Error in deafen_voice_member: {e}")
            return {"success": False, "error": str(e)}

    @app.tool()
    async def discord_monitor_voice_channel_activity(
        channel_id: str, include_timestamps: Optional[bool] = False
    ) -> Dict[str, Any]:
        """Monitor current voice channel activity.

        Args:
            channel_id: The voice channel ID to monitor
            include_timestamps: Whether to include join/leave timestamps

        Returns:
            Success status with channel activity information
        """
        try:
            channel = client.get_channel(int(channel_id))
            if not isinstance(channel, discord.VoiceChannel):
                return {"success": False, "error": "Channel is not a voice channel"}

            guild = channel.guild
            bot_member = guild.get_member(client.user.id) if client.user else None
            has_access = (
                bot_member
                and (bot_voice_state := bot_member.voice)
                and bot_voice_state.channel == channel
                or any(c for c in guild.voice_channels if c == channel)
            )

            members_info = []
            for member in channel.members:
                member_data: Dict[str, Any] = {
                    "id": str(member.id),
                    "username": member.name,
                    "display_name": member.display_name,
                }

                if include_timestamps and member.voice:
                    member_data.update(
                        {
                            "muted": member.voice.mute,
                            "deafened": member.voice.deaf,
                            "self_muted": member.voice.self_mute,
                            "self_deafened": member.voice.self_deaf,
                            "self_stream": member.voice.self_stream,
                            "self_video": member.voice.self_video,
                        }
                    )

                members_info.append(member_data)

            activity_data = {
                "channel": {
                    "id": str(channel.id),
                    "name": channel.name,
                    "guild_id": str(guild.id),
                    "guild_name": guild.name,
                    "member_count": len(members_info),
                    "bitrate": channel.bitrate,
                    "user_limit": channel.user_limit,
                },
                "members": members_info,
                "total_active": len(members_info),
                "timestamp": discord.utils.utcnow().isoformat(),
            }

            return {
                "success": True,
                "data": activity_data,
            }
        except discord.Forbidden:
            return {"success": False, "error": "Bot lacks required permissions"}
        except discord.NotFound:
            return {"success": False, "error": "Channel not found"}
        except discord.HTTPException as e:
            return {"success": False, "error": f"Discord API error: {e}"}
        except Exception as e:
            logger.error(f"Error in monitor_voice_channel_activity: {e}")
            return {"success": False, "error": str(e)}
