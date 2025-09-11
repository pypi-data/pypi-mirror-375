"""Discord channel management FastMCP tools."""

from typing import Any, Dict, Optional
import discord
from loguru import logger

try:
    from fastmcp import FastMCP
except ImportError:
    logger.error("FastMCP not installed. Please run: uv add fastmcp>=2.12.0")
    raise


def register_channel_tools(app: FastMCP, client: discord.Client, config: Any) -> None:
    """Register Discord channel management tools with FastMCP app."""

    @app.tool()
    async def discord_list_channels(
        guild_id: str, channel_type: str = "all"
    ) -> Dict[str, Any]:
        """List all channels in a Discord server."""
        try:
            guild = client.get_guild(int(guild_id))
            if not guild:
                return {
                    "success": False,
                    "error": f"Guild {guild_id} not found or bot not in guild",
                }

            channels = []
            type_filter = channel_type.lower() if channel_type != "all" else None

            for channel in guild.channels:
                if isinstance(channel, discord.abc.GuildChannel):
                    # Apply type filter
                    if type_filter:
                        if type_filter == "text" and not isinstance(
                            channel, discord.TextChannel
                        ):
                            continue
                        elif type_filter == "voice" and not isinstance(
                            channel, discord.VoiceChannel
                        ):
                            continue
                        elif type_filter == "category" and not isinstance(
                            channel, discord.CategoryChannel
                        ):
                            continue
                        elif type_filter == "forum" and not isinstance(
                            channel, discord.ForumChannel
                        ):
                            continue
                        elif type_filter == "thread" and not isinstance(
                            channel, discord.Thread
                        ):
                            continue

                    channel_info = {
                        "id": str(channel.id),
                        "name": channel.name,
                        "type": str(channel.type),
                        "position": channel.position,
                        "created_at": channel.created_at.isoformat(),
                    }

                    # Add type-specific information
                    if isinstance(channel, discord.TextChannel):
                        channel_info.update(
                            {
                                "topic": channel.topic,
                                "nsfw": channel.nsfw,
                                "slowmode_delay": channel.slowmode_delay,
                            }
                        )
                    elif isinstance(channel, discord.VoiceChannel):
                        channel_info.update(
                            {
                                "bitrate": channel.bitrate,
                                "user_limit": channel.user_limit,
                                "connected_members": len(channel.members),
                            }
                        )

                    channels.append(channel_info)

            # Sort channels by position and name
            channels.sort(key=lambda x: (x.get("position", 0), x.get("name", "")))

            return {
                "success": True,
                "data": {
                    "channels": channels,
                    "total_count": len(channels),
                    "guild_name": guild.name,
                    "filter": channel_type,
                },
            }

        except ValueError:
            return {"success": False, "error": "Invalid guild ID format"}
        except Exception as e:
            logger.error(f"Error listing channels: {e}")
            return {"success": False, "error": f"Unexpected error: {e}"}

    @app.tool()
    async def discord_create_category(
        guildId: str,
        name: str,
        position: Optional[int] = None,
        reason: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Creates a new category in a Discord server."""
        try:
            guild = client.get_guild(int(guildId))
            if not guild:
                return {
                    "success": False,
                    "error": f"Guild {guildId} not found or bot not in guild",
                }

            # Check bot permissions
            bot_member = guild.get_member(client.user.id) if client.user else None
            if not bot_member or not bot_member.guild_permissions.manage_channels:
                return {
                    "success": False,
                    "error": "Bot lacks manage_channels permission",
                }

            # Create category
            if position is not None:
                category = await guild.create_category_channel(
                    name=name,
                    position=position,
                    reason=reason or "Created via Discord MCP",
                )
            else:
                category = await guild.create_category_channel(
                    name=name, reason=reason or "Created via Discord MCP"
                )

            return {
                "success": True,
                "data": {
                    "category_id": str(category.id),
                    "name": category.name,
                    "position": category.position,
                    "guild_id": str(guild.id),
                },
            }

        except ValueError:
            return {"success": False, "error": "Invalid guild ID format"}
        except discord.Forbidden:
            return {
                "success": False,
                "error": "Bot lacks permission to create categories",
            }
        except discord.HTTPException as e:
            return {"success": False, "error": f"Discord API error: {e}"}
        except Exception as e:
            logger.error(f"Error creating category: {e}")
            return {"success": False, "error": f"Unexpected error: {e}"}

    @app.tool()
    async def discord_edit_category(
        categoryId: str,
        name: Optional[str] = None,
        position: Optional[int] = None,
        reason: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Edits an existing Discord category (name and position)."""
        try:
            category = client.get_channel(int(categoryId))
            if not category:
                return {"success": False, "error": f"Category {categoryId} not found"}

            if not isinstance(category, discord.CategoryChannel):
                return {"success": False, "error": "Channel is not a category"}

            # Check bot permissions
            bot_member = (
                category.guild.get_member(client.user.id) if client.user else None
            )
            if not bot_member or not bot_member.guild_permissions.manage_channels:
                return {
                    "success": False,
                    "error": "Bot lacks manage_channels permission",
                }

            # Prepare edit arguments
            edit_kwargs = {}
            if name is not None:
                edit_kwargs["name"] = name
            if position is not None:
                edit_kwargs["position"] = position
            if reason:
                edit_kwargs["reason"] = reason

            await category.edit(**edit_kwargs)

            return {
                "success": True,
                "data": {
                    "category_id": str(category.id),
                    "name": category.name,
                    "position": category.position,
                    "edited": True,
                },
            }

        except ValueError:
            return {"success": False, "error": "Invalid category ID format"}
        except discord.Forbidden:
            return {
                "success": False,
                "error": "Bot lacks permission to edit categories",
            }
        except discord.HTTPException as e:
            return {"success": False, "error": f"Discord API error: {e}"}
        except Exception as e:
            logger.error(f"Error editing category: {e}")
            return {"success": False, "error": f"Unexpected error: {e}"}

    @app.tool()
    async def discord_delete_category(
        categoryId: str, reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """Deletes a Discord category by ID."""
        try:
            category = client.get_channel(int(categoryId))
            if not category:
                return {"success": False, "error": f"Category {categoryId} not found"}

            if not isinstance(category, discord.CategoryChannel):
                return {"success": False, "error": "Channel is not a category"}

            # Check bot permissions
            bot_member = (
                category.guild.get_member(client.user.id) if client.user else None
            )
            if not bot_member or not bot_member.guild_permissions.manage_channels:
                return {
                    "success": False,
                    "error": "Bot lacks manage_channels permission",
                }

            category_name = category.name
            await category.delete(reason=reason or "Deleted via Discord MCP")

            return {
                "success": True,
                "data": {
                    "deleted_category_id": str(categoryId),
                    "deleted_category_name": category_name,
                },
            }

        except ValueError:
            return {"success": False, "error": "Invalid category ID format"}
        except discord.Forbidden:
            return {
                "success": False,
                "error": "Bot lacks permission to delete categories",
            }
        except discord.HTTPException as e:
            return {"success": False, "error": f"Discord API error: {e}"}
        except Exception as e:
            logger.error(f"Error deleting category: {e}")
            return {"success": False, "error": f"Unexpected error: {e}"}

    @app.tool()
    async def discord_create_text_channel(
        guildId: str,
        channelName: str,
        topic: Optional[str] = None,
        categoryId: Optional[str] = None,
        reason: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Creates a new text channel in a Discord server with an optional topic."""
        try:
            guild = client.get_guild(int(guildId))
            if not guild:
                return {
                    "success": False,
                    "error": f"Guild {guildId} not found or bot not in guild",
                }

            # Check bot permissions
            bot_member = guild.get_member(client.user.id) if client.user else None
            if not bot_member or not bot_member.guild_permissions.manage_channels:
                return {
                    "success": False,
                    "error": "Bot lacks manage_channels permission",
                }

            # Get category if specified
            category = None
            if categoryId:
                category = guild.get_channel(int(categoryId))
                if not category or not isinstance(category, discord.CategoryChannel):
                    return {
                        "success": False,
                        "error": f"Invalid category ID {categoryId}",
                    }

            # Create text channel
            if topic is not None:
                text_channel = await guild.create_text_channel(
                    name=channelName,
                    topic=topic,
                    category=category,
                    reason=reason or "Created via Discord MCP",
                )
            else:
                text_channel = await guild.create_text_channel(
                    name=channelName,
                    category=category,
                    reason=reason or "Created via Discord MCP",
                )

            return {
                "success": True,
                "data": {
                    "channel_id": str(text_channel.id),
                    "name": text_channel.name,
                    "topic": text_channel.topic,
                    "guild_id": str(guild.id),
                    "category_id": str(categoryId) if categoryId else None,
                    "type": "text",
                },
            }

        except ValueError:
            return {"success": False, "error": "Invalid guild ID or category ID format"}
        except discord.Forbidden:
            return {
                "success": False,
                "error": "Bot lacks permission to create channels",
            }
        except discord.HTTPException as e:
            return {"success": False, "error": f"Discord API error: {e}"}
        except Exception as e:
            logger.error(f"Error creating text channel: {e}")
            return {"success": False, "error": f"Unexpected error: {e}"}

    @app.tool()
    async def discord_edit_channel(
        channelId: str,
        name: Optional[str] = None,
        topic: Optional[str] = None,
        categoryId: Optional[str] = None,
        reason: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Edits an existing Discord channel (name, topic, category)."""
        try:
            channel = client.get_channel(int(channelId))
            if not channel:
                return {"success": False, "error": f"Channel {channelId} not found"}

            if not isinstance(
                channel,
                (discord.TextChannel, discord.VoiceChannel, discord.ForumChannel),
            ):
                return {
                    "success": False,
                    "error": "Channel type not supported for editing",
                }

            # Check bot permissions
            bot_member = (
                channel.guild.get_member(client.user.id) if client.user else None
            )
            if not bot_member or not bot_member.guild_permissions.manage_channels:
                return {
                    "success": False,
                    "error": "Bot lacks manage_channels permission",
                }

            # Get category if specified
            category = None
            if categoryId:
                category = channel.guild.get_channel(int(categoryId))
                if not category or not isinstance(category, discord.CategoryChannel):
                    return {
                        "success": False,
                        "error": f"Invalid category ID {categoryId}",
                    }

            # Prepare edit arguments
            edit_kwargs = {}
            if name is not None:
                edit_kwargs["name"] = name
            if topic is not None and isinstance(channel, discord.TextChannel):
                edit_kwargs["topic"] = topic
            if category is not None:
                edit_kwargs["category"] = category
            if reason:
                edit_kwargs["reason"] = reason

            await channel.edit(**edit_kwargs)

            return {
                "success": True,
                "data": {
                    "channel_id": str(channel.id),
                    "name": channel.name,
                    "topic": getattr(channel, "topic", None),
                    "category_id": str(category.id) if category else None,
                    "edited": True,
                },
            }

        except ValueError:
            return {
                "success": False,
                "error": "Invalid channel ID or category ID format",
            }
        except discord.Forbidden:
            return {"success": False, "error": "Bot lacks permission to edit channels"}
        except discord.HTTPException as e:
            return {"success": False, "error": f"Discord API error: {e}"}
        except Exception as e:
            logger.error(f"Error editing channel: {e}")
            return {"success": False, "error": f"Unexpected error: {e}"}

    @app.tool()
    async def discord_delete_channel(
        channelId: str, reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """Deletes a Discord channel with an optional reason."""
        try:
            channel = client.get_channel(int(channelId))
            if not channel:
                return {"success": False, "error": f"Channel {channelId} not found"}

            if not isinstance(
                channel,
                (discord.TextChannel, discord.VoiceChannel, discord.ForumChannel),
            ):
                return {
                    "success": False,
                    "error": "Channel type not supported for deletion",
                }

            # Check bot permissions
            bot_member = (
                channel.guild.get_member(client.user.id) if client.user else None
            )
            if not bot_member or not bot_member.guild_permissions.manage_channels:
                return {
                    "success": False,
                    "error": "Bot lacks manage_channels permission",
                }

            channel_name = channel.name
            await channel.delete(reason=reason or "Deleted via Discord MCP")

            return {
                "success": True,
                "data": {
                    "deleted_channel_id": str(channelId),
                    "deleted_channel_name": channel_name,
                },
            }

        except ValueError:
            return {"success": False, "error": "Invalid channel ID format"}
        except discord.Forbidden:
            return {
                "success": False,
                "error": "Bot lacks permission to delete channels",
            }
        except discord.HTTPException as e:
            return {"success": False, "error": f"Discord API error: {e}"}
        except Exception as e:
            logger.error(f"Error deleting channel: {e}")
            return {"success": False, "error": f"Unexpected error: {e}"}

    @app.tool()
    async def discord_create_channel_under_category(
        guildId: str,
        channelName: str,
        channelType: str,
        categoryId: str,
        topic: Optional[str] = None,
        reason: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Creates a new channel (text, voice, or forum) and places it under a specific category."""
        try:
            guild = client.get_guild(int(guildId))
            if not guild:
                return {
                    "success": False,
                    "error": f"Guild {guildId} not found or bot not in guild",
                }

            # Check bot permissions
            bot_member = guild.get_member(client.user.id) if client.user else None
            if not bot_member or not bot_member.guild_permissions.manage_channels:
                return {
                    "success": False,
                    "error": "Bot lacks manage_channels permission",
                }

            # Get category
            category = guild.get_channel(int(categoryId))
            if not category or not isinstance(category, discord.CategoryChannel):
                return {
                    "success": False,
                    "error": f"Invalid category ID {categoryId}",
                }

            # Create channel based on type
            if channelType.lower() == "text":
                if topic is not None:
                    channel = await guild.create_text_channel(
                        name=channelName,
                        topic=topic,
                        category=category,
                        reason=reason or "Created via Discord MCP",
                    )
                else:
                    channel = await guild.create_text_channel(
                        name=channelName,
                        category=category,
                        reason=reason or "Created via Discord MCP",
                    )
            elif channelType.lower() == "voice":
                channel = await guild.create_voice_channel(
                    name=channelName,
                    category=category,
                    reason=reason or "Created via Discord MCP",
                )
            elif channelType.lower() == "forum":
                if topic is not None:
                    channel = await guild.create_forum_channel(
                        name=channelName,
                        topic=topic,
                        category=category,
                        reason=reason or "Created via Discord MCP",
                    )
                else:
                    channel = await guild.create_forum_channel(
                        name=channelName,
                        category=category,
                        reason=reason or "Created via Discord MCP",
                    )
            else:
                return {
                    "success": False,
                    "error": f"Unsupported channel type: {channelType}",
                }

            return {
                "success": True,
                "data": {
                    "channel_id": str(channel.id),
                    "name": channel.name,
                    "type": channelType.lower(),
                    "guild_id": str(guild.id),
                    "category_id": str(categoryId),
                    "topic": getattr(channel, "topic", None),
                },
            }

        except ValueError:
            return {"success": False, "error": "Invalid guild ID or category ID format"}
        except discord.Forbidden:
            return {
                "success": False,
                "error": "Bot lacks permission to create channels",
            }
        except discord.HTTPException as e:
            return {"success": False, "error": f"Discord API error: {e}"}
        except Exception as e:
            logger.error(f"Error creating channel under category: {e}")
            return {"success": False, "error": f"Unexpected error: {e}"}

    @app.tool()
    async def discord_move_channel_to_category(
        channelId: str, categoryId: str, reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """Moves an existing channel to a different category."""
        try:
            channel = client.get_channel(int(channelId))
            if not channel:
                return {"success": False, "error": f"Channel {channelId} not found"}

            if not isinstance(
                channel,
                (discord.TextChannel, discord.VoiceChannel, discord.ForumChannel),
            ):
                return {
                    "success": False,
                    "error": "Channel type not supported for moving",
                }

            # Get category
            category = channel.guild.get_channel(int(categoryId))
            if not category or not isinstance(category, discord.CategoryChannel):
                return {
                    "success": False,
                    "error": f"Invalid category ID {categoryId}",
                }

            # Check bot permissions
            bot_member = (
                channel.guild.get_member(client.user.id) if client.user else None
            )
            if not bot_member or not bot_member.guild_permissions.manage_channels:
                return {
                    "success": False,
                    "error": "Bot lacks manage_channels permission",
                }

            # Move channel to category
            await channel.edit(
                category=category, reason=reason or "Moved via Discord MCP"
            )

            return {
                "success": True,
                "data": {
                    "channel_id": str(channel.id),
                    "channel_name": channel.name,
                    "new_category_id": str(categoryId),
                    "new_category_name": category.name,
                    "moved": True,
                },
            }

        except ValueError:
            return {
                "success": False,
                "error": "Invalid channel ID or category ID format",
            }
        except discord.Forbidden:
            return {"success": False, "error": "Bot lacks permission to move channels"}
        except discord.HTTPException as e:
            return {"success": False, "error": f"Discord API error: {e}"}
        except Exception as e:
            logger.error(f"Error moving channel to category: {e}")
            return {"success": False, "error": f"Unexpected error: {e}"}

    # Log channel tool registration
    logger.info(
        "Registered Discord channel tools: list_channels, create_category, edit_category, delete_category, create_text_channel, edit_channel, delete_channel, create_channel_under_category, move_channel_to_category"
    )
