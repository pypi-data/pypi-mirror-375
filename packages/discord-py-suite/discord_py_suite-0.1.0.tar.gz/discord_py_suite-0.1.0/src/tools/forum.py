"""Discord forum management FastMCP tools."""

from typing import Any, Dict, Optional, List
import discord
from loguru import logger
from ..types_helper import safe_isoformat

try:
    from fastmcp import FastMCP
except ImportError:
    logger.error("FastMCP not installed. Please run: uv add fastmcp>=2.12.0")
    raise


def register_forum_tools(app: FastMCP, client: discord.Client, config: Any) -> None:
    """Register Discord forum management tools with FastMCP app."""

    @app.tool()
    async def discord_get_forum_channels(guildId: str) -> Dict[str, Any]:
        """List all forum channels in a Discord guild."""
        try:
            guild_id = int(guildId)
            guild = client.get_guild(guild_id)
            if not guild:
                return {
                    "success": False,
                    "error": f"Guild {guild_id} not found or bot not in guild",
                }

            # Check bot permissions
            bot_member = guild.get_member(client.user.id) if client.user else None
            if not bot_member or not bot_member.guild_permissions.view_channel:
                return {"success": False, "error": "Bot lacks view_channel permission"}

            forum_channels = []
            for channel in guild.channels:
                # Check if this is a forum channel using isinstance
                if isinstance(channel, discord.ForumChannel):
                    forum_data = {
                        "channel_id": str(channel.id),
                        "name": channel.name,
                        "topic": channel.topic or "",
                        "position": channel.position,
                        "slowmode_delay": channel.slowmode_delay,
                        "topic_tags": [
                            {
                                "name": tag.name,
                                "emoji": str(tag.emoji) if tag.emoji else None,
                                "moderated": tag.moderated,
                            }
                            for tag in channel.available_tags
                        ],
                        "permissions_locked": getattr(
                            channel, "permissions_locked", False
                        ),
                        "nsfw": channel.nsfw,
                        "created_at": channel.created_at.isoformat(),
                    }
                    forum_channels.append(forum_data)

            return {
                "success": True,
                "data": {
                    "guild_id": str(guild_id),
                    "forum_channels": forum_channels,
                    "count": len(forum_channels),
                },
            }

        except ValueError:
            return {"success": False, "error": "Invalid guild ID format"}
        except discord.HTTPException as e:
            return {"success": False, "error": f"Discord API error: {e}"}
        except Exception as e:
            logger.error(f"Error getting forum channels: {e}")
            return {"success": False, "error": f"Unexpected error: {e}"}

    @app.tool()
    async def discord_create_forum_channel(
        guild_id: int,
        name: str,
        topic: Optional[str] = None,
        category_id: Optional[int] = None,
        position: Optional[int] = None,
        slowmode_delay: Optional[int] = None,
        topic_tags: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Create a forum channel in a Discord guild."""
        try:
            guild = client.get_guild(guild_id)
            if not guild:
                return {
                    "success": False,
                    "error": f"Guild {guild_id} not found or bot not in guild",
                }

            # Check bot permissions
            bot_member = guild.get_member(client.user.id) if client.user else None
            if not bot_member or not bot_member.guild_permissions.manage_channels:
                return {
                    "success": False,
                    "error": "Bot lacks manage_channels permission",
                }

            # Validate category if provided
            category = None
            if category_id:
                category = guild.get_channel(category_id)
                if not category or not isinstance(category, discord.CategoryChannel):
                    return {
                        "success": False,
                        "error": f"Invalid category ID {category_id}",
                    }

            # Create forum channel using py-cord's create_forum_channel method
            try:
                # Prepare forum channel kwargs for py-cord
                create_kwargs = {
                    "name": name,
                    "topic": topic or "Forum created via FastMCP",
                    "category": category,
                    "slowmode_delay": slowmode_delay or 0,
                    "reason": "Created by FastMCP tool",
                }

                # Add position if specified
                if position is not None:
                    create_kwargs["position"] = position

                # Use create_forum_channel for py-cord
                forum_channel = await guild.create_forum_channel(**create_kwargs)
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Failed to create forum channel: {e}",
                }

            # Add default forum tags if provided
            if topic_tags:
                try:
                    # Note: This may require additional setup depending on Discord.py version
                    # Forum tag creation might need to be handled differently
                    pass
                except Exception:
                    logger.warning("Could not set forum topic tags during creation")

            return {
                "success": True,
                "data": {
                    "channel_id": str(forum_channel.id),
                    "name": forum_channel.name,
                    "guild_id": str(guild_id),
                    "type": "forum",
                    "position": forum_channel.position,
                    "category_id": str(category_id) if category_id else None,
                },
            }

        except ValueError:
            return {"success": False, "error": "Invalid guild ID format"}
        except discord.Forbidden:
            return {
                "success": False,
                "error": "Bot lacks permission to create channels",
            }
        except discord.HTTPException as e:
            return {"success": False, "error": f"Discord API error: {e}"}
        except Exception as e:
            logger.error(f"Error creating forum channel: {e}")
            return {"success": False, "error": f"Unexpected error: {e}"}

    @app.tool()
    async def discord_modify_forum_channel(
        channel_id: int,
        name: Optional[str] = None,
        position: Optional[int] = None,
        topic: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Modify settings of a forum channel."""
        try:
            channel = client.get_channel(channel_id)
            if not channel:
                return {"success": False, "error": f"Channel {channel_id} not found"}

            # Check if channel is a forum channel (py-cord compatibility)
            if not isinstance(channel, discord.ForumChannel):
                return {"success": False, "error": "Channel is not a forum channel"}

            # Check bot permissions
            bot_member = (
                channel.guild.get_member(client.user.id) if client.user else None
            )
            if not bot_member or not bot_member.guild_permissions.manage_channels:
                return {
                    "success": False,
                    "error": "Bot lacks manage_channels permission",
                }

            # Prepare modification arguments
            modify_kwargs: Dict[str, Any] = {}
            if name is not None:
                modify_kwargs["name"] = name
            if position is not None:
                modify_kwargs["position"] = position
            if topic is not None:
                modify_kwargs["topic"] = topic

            await channel.edit(**modify_kwargs)

            return {
                "success": True,
                "data": {
                    "channel_id": str(channel_id),
                    "name": channel.name,
                    "topic": channel.topic or "",
                    "position": channel.position,
                    "modified": True,
                },
            }

        except ValueError:
            return {"success": False, "error": "Invalid channel ID format"}
        except discord.Forbidden:
            return {
                "success": False,
                "error": "Bot lacks permission to modify channels",
            }
        except discord.HTTPException as e:
            return {"success": False, "error": f"Discord API error: {e}"}
        except Exception as e:
            logger.error(f"Error modifying forum channel: {e}")
            return {"success": False, "error": f"Unexpected error: {e}"}

    @app.tool()
    async def discord_create_forum_post(
        forumChannelId: str,
        title: str,
        content: str,
        tags: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Create a new forum thread/post."""
        try:
            channel_id = int(forumChannelId)
            channel = client.get_channel(channel_id)
            if not channel:
                return {"success": False, "error": f"Channel {channel_id} not found"}

            if not isinstance(channel, discord.ForumChannel):
                return {"success": False, "error": "Channel is not a forum channel"}

            # Check bot permissions
            bot_member = (
                channel.guild.get_member(client.user.id) if client.user else None
            )
            if not bot_member or not bot_member.guild_permissions.send_messages:
                return {"success": False, "error": "Bot lacks send_messages permission"}
            if not bot_member or not bot_member.guild_permissions.manage_threads:
                return {
                    "success": False,
                    "error": "Bot lacks manage_threads permission",
                }

            # Create the forum thread with starter message using py-cord API
            thread = await channel.create_thread(
                name=title[:100],  # Discord limits thread names to 100 chars
                reason="Created via Discord MCP",
                auto_archive_duration=1440,  # 24 hours
            )

            # Send the initial message to the thread
            message = await thread.send(content)

            # Apply tags if provided (this might need forum-specific implementation)
            if tags and hasattr(channel, "available_tags"):
                try:
                    # Map tag names to tag objects
                    available_tags = {tag.name: tag for tag in channel.available_tags}
                    applied_tag_objects = [
                        available_tags[tag_name]
                        for tag_name in tags
                        if tag_name in available_tags
                    ]

                    if applied_tag_objects:
                        await thread.edit(applied_tags=applied_tag_objects)
                except Exception as e:
                    logger.warning(f"Could not apply tags to forum thread: {e}")

            return {
                "success": True,
                "data": {
                    "thread_id": str(thread.id),
                    "channel_id": str(channel_id),
                    "title": thread.name,
                    "owner_id": str(thread.owner_id) if thread.owner_id else None,
                    "created_at": thread.created_at.isoformat()
                    if thread.created_at
                    else None,
                    "message_count": thread.message_count,
                    "applied_tags": tags or [],
                },
            }

        except ValueError:
            return {"success": False, "error": "Invalid channel ID format"}
        except discord.Forbidden:
            return {"success": False, "error": "Bot lacks permission to create threads"}
        except discord.HTTPException as e:
            return {"success": False, "error": f"Discord API error: {e}"}
        except Exception as e:
            logger.error(f"Error creating forum post: {e}")
            return {"success": False, "error": f"Unexpected error: {e}"}

    @app.tool()
    async def discord_reply_to_forum(thread_id: int, content: str) -> Dict[str, Any]:
        """Reply to an existing forum thread."""
        try:
            thread = client.get_channel(thread_id)
            if not thread:
                return {"success": False, "error": f"Thread {thread_id} not found"}

            # Check if it's a thread
            if not isinstance(thread, discord.Thread):
                return {"success": False, "error": "Channel is not a thread"}

            # Check bot permissions
            bot_member = (
                thread.guild.get_member(client.user.id) if client.user else None
            )
            if (
                not bot_member
                or not bot_member.guild_permissions.send_messages_in_threads
            ):
                return {
                    "success": False,
                    "error": "Bot lacks send_messages_in_threads permission",
                }

            # Send reply message
            message = await thread.send(content)

            return {
                "success": True,
                "data": {
                    "message_id": str(message.id),
                    "thread_id": str(thread_id),
                    "author_id": str(message.author.id),
                    "content": message.content,
                    "created_at": message.created_at.isoformat(),
                },
            }

        except ValueError:
            return {"success": False, "error": "Invalid thread ID format"}
        except discord.Forbidden:
            return {
                "success": False,
                "error": "Bot lacks permission to reply in threads",
            }
        except discord.HTTPException as e:
            return {"success": False, "error": f"Discord API error: {e}"}
        except Exception as e:
            logger.error(f"Error replying to forum: {e}")
            return {"success": False, "error": f"Unexpected error: {e}"}

    @app.tool()
    async def discord_get_forum_post(thread_id: int) -> Dict[str, Any]:
        """Get details of a forum thread post."""
        try:
            thread = client.get_channel(thread_id)
            if not thread:
                return {"success": False, "error": f"Thread {thread_id} not found"}

            if not isinstance(thread, discord.Thread):
                return {"success": False, "error": "Channel is not a thread"}

            # Get initial message
            try:
                startup_message = None
                # Get the starter message (first message in forum thread)
                async for message in thread.history(limit=1, oldest_first=True):
                    startup_message = message
                    break
            except Exception:
                startup_message = None

            thread_data: Dict[str, Any] = {
                "thread_id": str(thread.id),
                "name": thread.name,
                "parent_channel_id": str(thread.parent.id) if thread.parent else None,
                "owner_id": str(thread.owner_id) if thread.owner_id else None,
                "message_count": thread.message_count,
                "member_count": len(thread.members),
                "created_at": safe_isoformat(thread.created_at),
                "archived": thread.archived,
                "locked": thread.locked,
                "slowmode_delay": thread.slowmode_delay,
                "type": str(thread.type),
                "applied_tags": [],  # If available
                "is_forum_post": thread.type == discord.ChannelType.public_thread,
                "last_message_id": str(thread.last_message_id)
                if thread.last_message_id
                else None,
            }

            if startup_message:
                thread_data["startup_message"] = {
                    "id": str(startup_message.id),
                    "content": startup_message.content,
                    "author": {
                        "id": str(startup_message.author.id),
                        "name": startup_message.author.name,
                        "discriminator": startup_message.author.discriminator,
                    },
                    "created_at": startup_message.created_at.isoformat(),
                    "attachments": [
                        {
                            "filename": attachment.filename,
                            "url": attachment.url,
                            "proxy_url": attachment.proxy_url,
                        }
                        for attachment in startup_message.attachments
                    ],
                }

            return {"success": True, "data": thread_data}

        except ValueError:
            return {"success": False, "error": "Invalid thread ID format"}
        except discord.HTTPException as e:
            return {"success": False, "error": f"Discord API error: {e}"}
        except Exception as e:
            logger.error(f"Error getting forum post: {e}")
            return {"success": False, "error": f"Unexpected error: {e}"}

    @app.tool()
    async def discord_list_forum_posts(
        channel_id: int,
        limit: Optional[int] = 50,
        before: Optional[int] = None,
        after: Optional[int] = None,
    ) -> Dict[str, Any]:
        """List threads/posts in a forum channel."""
        try:
            channel = client.get_channel(channel_id)
            if not channel:
                return {"success": False, "error": f"Channel {channel_id} not found"}

            if not isinstance(channel, discord.ForumChannel):
                return {"success": False, "error": "Channel is not a forum channel"}

            # Check bot permissions
            bot_member = (
                channel.guild.get_member(client.user.id) if client.user else None
            )
            if not bot_member or not bot_member.guild_permissions.view_channel:
                return {"success": False, "error": "Bot lacks view_channel permission"}

            # Get threads with pagination - use guild.threads for py-cord
            threads_data = []

            # For forum channels, we need to get active threads first
            if hasattr(channel, "threads"):
                # Get active threads
                for thread in channel.threads:
                    if thread.parent_id == channel.id:
                        thread_info = {
                            "thread_id": str(thread.id),
                            "name": thread.name,
                            "owner_id": str(thread.owner_id)
                            if thread.owner_id
                            else None,
                            "message_count": thread.message_count,
                            "member_count": len(thread.members)
                            if hasattr(thread, "members")
                            else 0,
                            "created_at": thread.created_at.isoformat()
                            if thread.created_at
                            else None,
                            "archived": thread.archived,
                            "locked": thread.locked,
                            "auto_archive_duration": thread.auto_archive_duration,
                        }
                        threads_data.append(thread_info)

            # Also try to get archived threads if available
            try:
                archived_threads = []
                async for thread in channel.archived_threads(limit=limit):
                    if len(threads_data) < (limit or 50):
                        thread_info = {
                            "thread_id": str(thread.id),
                            "name": thread.name,
                            "owner_id": str(thread.owner_id)
                            if thread.owner_id
                            else None,
                            "message_count": thread.message_count,
                            "member_count": len(thread.members)
                            if hasattr(thread, "members")
                            else 0,
                            "created_at": thread.created_at.isoformat()
                            if thread.created_at
                            else None,
                            "archived": thread.archived,
                            "locked": thread.locked,
                            "auto_archive_duration": thread.auto_archive_duration,
                        }
                        threads_data.append(thread_info)
            except Exception:
                # If archived_threads doesn't work, just use what we have
                pass

            return {
                "success": True,
                "data": {
                    "channel_id": str(channel_id),
                    "threads": threads_data,
                    "count": len(threads_data),
                    "limit": limit,
                },
            }

        except ValueError:
            return {"success": False, "error": "Invalid channel ID format"}
        except discord.HTTPException as e:
            return {"success": False, "error": f"Discord API error: {e}"}
        except Exception as e:
            logger.error(f"Error listing forum posts: {e}")
            return {"success": False, "error": f"Unexpected error: {e}"}

    @app.tool()
    async def discord_delete_forum_post(thread_id: int) -> Dict[str, Any]:
        """Delete a forum thread."""
        try:
            thread = client.get_channel(thread_id)
            if not thread:
                return {"success": False, "error": f"Thread {thread_id} not found"}

            if not isinstance(thread, discord.Thread):
                return {"success": False, "error": "Channel is not a thread"}

            # Check bot permissions
            bot_member = (
                thread.guild.get_member(client.user.id) if client.user else None
            )
            if not bot_member or not bot_member.guild_permissions.manage_threads:
                return {
                    "success": False,
                    "error": "Bot lacks manage_threads permission",
                }

            thread_name = thread.name
            await thread.delete()

            return {
                "success": True,
                "data": {
                    "deleted_thread_id": str(thread_id),
                    "deleted_thread_name": thread_name,
                },
            }

        except ValueError:
            return {"success": False, "error": "Invalid thread ID format"}
        except discord.Forbidden:
            return {"success": False, "error": "Bot lacks permission to delete threads"}
        except discord.HTTPException as e:
            return {"success": False, "error": f"Discord API error: {e}"}
        except Exception as e:
            logger.error(f"Error deleting forum post: {e}")
            return {"success": False, "error": f"Unexpected error: {e}"}

    @app.tool()
    async def discord_archive_forum_post(thread_id: int) -> Dict[str, Any]:
        """Archive a forum thread."""
        try:
            thread = client.get_channel(thread_id)
            if not thread:
                return {"success": False, "error": f"Thread {thread_id} not found"}

            if not isinstance(thread, discord.Thread):
                return {"success": False, "error": "Channel is not a thread"}

            # Check bot permissions
            bot_member = (
                thread.guild.get_member(client.user.id) if client.user else None
            )
            if not bot_member or not bot_member.guild_permissions.manage_threads:
                return {
                    "success": False,
                    "error": "Bot lacks manage_threads permission",
                }

            if thread.archived:
                return {"success": False, "error": "Thread is already archived"}

            await thread.edit(archived=True)

            return {
                "success": True,
                "data": {
                    "thread_id": str(thread_id),
                    "archived": True,
                    "archived_at": safe_isoformat(getattr(thread, "archived_at", None)),
                },
            }

        except ValueError:
            return {"success": False, "error": "Invalid thread ID format"}
        except discord.Forbidden:
            return {
                "success": False,
                "error": "Bot lacks permission to archive threads",
            }
        except discord.HTTPException as e:
            return {"success": False, "error": f"Discord API error: {e}"}
        except Exception as e:
            logger.error(f"Error archiving forum post: {e}")
            return {"success": False, "error": f"Unexpected error: {e}"}

    @app.tool()
    async def discord_unarchive_forum_post(thread_id: int) -> Dict[str, Any]:
        """Unarchive a forum thread."""
        try:
            thread = client.get_channel(thread_id)
            if not thread:
                return {"success": False, "error": f"Thread {thread_id} not found"}

            if not isinstance(thread, discord.Thread):
                return {"success": False, "error": "Channel is not a thread"}

            # Check bot permissions
            bot_member = (
                thread.guild.get_member(client.user.id) if client.user else None
            )
            if not bot_member or not bot_member.guild_permissions.manage_threads:
                return {
                    "success": False,
                    "error": "Bot lacks manage_threads permission",
                }

            if not thread.archived:
                return {"success": False, "error": "Thread is not archived"}

            await thread.edit(archived=False)

            return {
                "success": True,
                "data": {
                    "thread_id": str(thread_id),
                    "archived": False,
                    "archived_at": None,
                },
            }

        except ValueError:
            return {"success": False, "error": "Invalid thread ID format"}
        except discord.Forbidden:
            return {
                "success": False,
                "error": "Bot lacks permission to unarchive threads",
            }
        except discord.HTTPException as e:
            return {"success": False, "error": f"Discord API error: {e}"}
        except Exception as e:
            logger.error(f"Error unarchiving forum post: {e}")
            return {"success": False, "error": f"Unexpected error: {e}"}

    @app.tool()
    async def discord_lock_forum_post(thread_id: int) -> Dict[str, Any]:
        """Lock a forum thread."""
        try:
            thread = client.get_channel(thread_id)
            if not thread:
                return {"success": False, "error": f"Thread {thread_id} not found"}

            if not isinstance(thread, discord.Thread):
                return {"success": False, "error": "Channel is not a thread"}

            # Check bot permissions
            bot_member = (
                thread.guild.get_member(client.user.id) if client.user else None
            )
            if not bot_member or not bot_member.guild_permissions.manage_threads:
                return {
                    "success": False,
                    "error": "Bot lacks manage_threads permission",
                }

            if thread.locked:
                return {"success": False, "error": "Thread is already locked"}

            await thread.edit(locked=True)

            return {
                "success": True,
                "data": {
                    "thread_id": str(thread_id),
                    "locked": True,
                },
            }

        except ValueError:
            return {"success": False, "error": "Invalid thread ID format"}
        except discord.Forbidden:
            return {"success": False, "error": "Bot lacks permission to lock threads"}
        except discord.HTTPException as e:
            return {"success": False, "error": f"Discord API error: {e}"}
        except Exception as e:
            logger.error(f"Error locking forum post: {e}")
            return {"success": False, "error": f"Unexpected error: {e}"}

    @app.tool()
    async def discord_unlock_forum_post(thread_id: int) -> Dict[str, Any]:
        """Unlock a forum thread."""
        try:
            thread = client.get_channel(thread_id)
            if not thread:
                return {"success": False, "error": f"Thread {thread_id} not found"}

            if not isinstance(thread, discord.Thread):
                return {"success": False, "error": "Channel is not a thread"}

            # Check bot permissions
            bot_member = (
                thread.guild.get_member(client.user.id) if client.user else None
            )
            if not bot_member or not bot_member.guild_permissions.manage_threads:
                return {
                    "success": False,
                    "error": "Bot lacks manage_threads permission",
                }

            if not thread.locked:
                return {"success": False, "error": "Thread is not locked"}

            await thread.edit(locked=False)

            return {
                "success": True,
                "data": {
                    "thread_id": str(thread_id),
                    "locked": False,
                },
            }

        except ValueError:
            return {"success": False, "error": "Invalid thread ID format"}
        except discord.Forbidden:
            return {"success": False, "error": "Bot lacks permission to unlock threads"}
        except discord.HTTPException as e:
            return {"success": False, "error": f"Discord API error: {e}"}
        except Exception as e:
            logger.error(f"Error unlocking forum post: {e}")
            return {"success": False, "error": f"Unexpected error: {e}"}

    @app.tool()
    async def discord_list_public_archived_threads(
        channel_id: int,
        before: Optional[int] = None,
        limit: Optional[int] = 50,
    ) -> Dict[str, Any]:
        """List public archived threads in a channel."""
        try:
            channel = client.get_channel(channel_id)
            if not channel:
                return {"success": False, "error": f"Channel {channel_id} not found"}

            # Check if channel supports threads
            if not hasattr(channel, "archived_threads"):
                return {
                    "success": False,
                    "error": "Channel does not support archived threads",
                }

            # Check bot permissions
            if hasattr(channel, "guild") and channel.guild:
                bot_member = (
                    channel.guild.get_member(client.user.id) if client.user else None
                )
                if not bot_member or not bot_member.guild_permissions.view_channel:
                    return {
                        "success": False,
                        "error": "Bot lacks view_channel permission",
                    }

            # Convert before parameter to Snowflake if provided
            before_snowflake = None
            if before:
                try:
                    before_snowflake = discord.Object(id=before)
                except:
                    return {
                        "success": False,
                        "error": "Invalid before parameter format",
                    }

            # Get archived threads
            threads = []
            async for thread in channel.archived_threads(
                before=before_snowflake, limit=limit
            ):
                # Filter for public threads only
                if thread.type == discord.ChannelType.public_thread:
                    thread_data = {
                        "id": str(thread.id),
                        "name": thread.name,
                        "owner_id": str(thread.owner_id) if thread.owner_id else None,
                        "parent_id": str(thread.parent_id)
                        if thread.parent_id
                        else None,
                        "message_count": thread.message_count,
                        "member_count": len(thread.members)
                        if hasattr(thread, "members")
                        else 0,
                        "created_at": safe_isoformat(thread.created_at),
                        "archived_at": safe_isoformat(
                            getattr(thread, "archived_at", None)
                        ),
                        "auto_archive_duration": thread.auto_archive_duration,
                        "locked": thread.locked,
                        "type": str(thread.type),
                    }
                    threads.append(thread_data)

            return {
                "success": True,
                "data": {
                    "channel_id": str(channel_id),
                    "threads": threads,
                    "count": len(threads),
                    "has_more": len(threads) == limit if limit else False,
                },
            }

        except ValueError:
            return {"success": False, "error": "Invalid channel ID format"}
        except discord.HTTPException as e:
            return {"success": False, "error": f"Discord API error: {e}"}
        except Exception as e:
            logger.error(f"Error listing public archived threads: {e}")
            return {"success": False, "error": f"Unexpected error: {e}"}

    @app.tool()
    async def discord_list_private_archived_threads(
        channel_id: int,
        before: Optional[int] = None,
        limit: Optional[int] = 50,
    ) -> Dict[str, Any]:
        """List private archived threads in a channel."""
        try:
            channel = client.get_channel(channel_id)
            if not channel:
                return {"success": False, "error": f"Channel {channel_id} not found"}

            # Check if channel supports threads
            if not hasattr(channel, "archived_threads"):
                return {
                    "success": False,
                    "error": "Channel does not support archived threads",
                }

            # Check bot permissions
            if hasattr(channel, "guild") and channel.guild:
                bot_member = (
                    channel.guild.get_member(client.user.id) if client.user else None
                )
                if not bot_member or not bot_member.guild_permissions.view_channel:
                    return {
                        "success": False,
                        "error": "Bot lacks view_channel permission",
                    }

            # Convert before parameter to Snowflake if provided
            before_snowflake = None
            if before:
                try:
                    before_snowflake = discord.Object(id=before)
                except:
                    return {
                        "success": False,
                        "error": "Invalid before parameter format",
                    }

            # Get archived threads
            threads = []
            async for thread in channel.archived_threads(
                before=before_snowflake, limit=limit
            ):
                # Filter for private threads only
                if thread.type == discord.ChannelType.private_thread:
                    thread_data = {
                        "id": str(thread.id),
                        "name": thread.name,
                        "owner_id": str(thread.owner_id) if thread.owner_id else None,
                        "parent_id": str(thread.parent_id)
                        if thread.parent_id
                        else None,
                        "message_count": thread.message_count,
                        "member_count": len(thread.members)
                        if hasattr(thread, "members")
                        else 0,
                        "created_at": safe_isoformat(thread.created_at),
                        "archived_at": safe_isoformat(
                            getattr(thread, "archived_at", None)
                        ),
                        "auto_archive_duration": thread.auto_archive_duration,
                        "locked": thread.locked,
                        "type": str(thread.type),
                    }
                    threads.append(thread_data)

            return {
                "success": True,
                "data": {
                    "channel_id": str(channel_id),
                    "threads": threads,
                    "count": len(threads),
                    "has_more": len(threads) == limit if limit else False,
                },
            }

        except ValueError:
            return {"success": False, "error": "Invalid channel ID format"}
        except discord.HTTPException as e:
            return {"success": False, "error": f"Discord API error: {e}"}
        except Exception as e:
            logger.error(f"Error listing private archived threads: {e}")
            return {"success": False, "error": f"Unexpected error: {e}"}

    @app.tool()
    async def discord_list_joined_private_archived_threads(
        channel_id: int,
        before: Optional[int] = None,
        limit: Optional[int] = 50,
    ) -> Dict[str, Any]:
        """List private archived threads that the bot has joined."""
        try:
            channel = client.get_channel(channel_id)
            if not channel:
                return {"success": False, "error": f"Channel {channel_id} not found"}

            # Check if channel supports threads
            if not hasattr(channel, "archived_threads"):
                return {
                    "success": False,
                    "error": "Channel does not support archived threads",
                }

            # Check bot permissions
            if hasattr(channel, "guild") and channel.guild:
                bot_member = (
                    channel.guild.get_member(client.user.id) if client.user else None
                )
                if not bot_member or not bot_member.guild_permissions.view_channel:
                    return {
                        "success": False,
                        "error": "Bot lacks view_channel permission",
                    }

            # Convert before parameter to Snowflake if provided
            before_snowflake = None
            if before:
                try:
                    before_snowflake = discord.Object(id=before)
                except:
                    return {
                        "success": False,
                        "error": "Invalid before parameter format",
                    }

            # Get archived threads
            threads = []
            async for thread in channel.archived_threads(
                before=before_snowflake, limit=limit
            ):
                # Filter for private threads that the bot has joined
                if (
                    thread.type == discord.ChannelType.private_thread
                    and hasattr(thread, "members")
                    and client.user
                    and any(member.id == client.user.id for member in thread.members)
                ):
                    thread_data = {
                        "id": str(thread.id),
                        "name": thread.name,
                        "owner_id": str(thread.owner_id) if thread.owner_id else None,
                        "parent_id": str(thread.parent_id)
                        if thread.parent_id
                        else None,
                        "message_count": thread.message_count,
                        "member_count": len(thread.members)
                        if hasattr(thread, "members")
                        else 0,
                        "created_at": safe_isoformat(thread.created_at),
                        "archived_at": safe_isoformat(
                            getattr(thread, "archived_at", None)
                        ),
                        "auto_archive_duration": thread.auto_archive_duration,
                        "locked": thread.locked,
                        "type": str(thread.type),
                    }
                    threads.append(thread_data)

            return {
                "success": True,
                "data": {
                    "channel_id": str(channel_id),
                    "threads": threads,
                    "count": len(threads),
                    "has_more": len(threads) == limit if limit else False,
                },
            }

        except ValueError:
            return {"success": False, "error": "Invalid channel ID format"}
        except discord.HTTPException as e:
            return {"success": False, "error": f"Discord API error: {e}"}
        except Exception as e:
            logger.error(f"Error listing joined private archived threads: {e}")
            return {"success": False, "error": f"Unexpected error: {e}"}

    @app.tool()
    async def discord_list_private_archived_threads(
        channel_id: int,
        before: Optional[str] = None,
        limit: Optional[int] = 50,
    ) -> Dict[str, Any]:
        """List private archived threads in a channel."""
        try:
            channel = client.get_channel(channel_id)
            if not channel:
                return {"success": False, "error": f"Channel {channel_id} not found"}

            # Check bot permissions
            bot_member = (
                channel.guild.get_member(client.user.id) if client.user else None
            )
            if not bot_member or not bot_member.guild_permissions.view_channel:
                return {"success": False, "error": "Bot lacks view_channel permission"}

            # Get archived threads
            threads = []
            async for thread in channel.archived_threads(
                private=True, before=before, limit=limit
            ):
                thread_data = {
                    "id": str(thread.id),
                    "name": thread.name,
                    "owner_id": str(thread.owner_id) if thread.owner_id else None,
                    "parent_id": str(thread.parent_id) if thread.parent_id else None,
                    "message_count": thread.message_count,
                    "member_count": len(thread.members)
                    if hasattr(thread, "members")
                    else 0,
                    "created_at": safe_isoformat(thread.created_at),
                    "archived_at": safe_isoformat(getattr(thread, "archived_at", None)),
                    "auto_archive_duration": thread.auto_archive_duration,
                    "locked": thread.locked,
                    "type": str(thread.type),
                }
                threads.append(thread_data)

            return {
                "success": True,
                "data": {
                    "channel_id": str(channel_id),
                    "threads": threads,
                    "count": len(threads),
                    "has_more": len(threads) == limit if limit else False,
                },
            }

        except ValueError:
            return {"success": False, "error": "Invalid channel ID format"}
        except discord.HTTPException as e:
            return {"success": False, "error": f"Discord API error: {e}"}
        except Exception as e:
            logger.error(f"Error listing private archived threads: {e}")
            return {"success": False, "error": f"Unexpected error: {e}"}

    @app.tool()
    async def discord_list_joined_private_archived_threads(
        channel_id: int,
        before: Optional[str] = None,
        limit: Optional[int] = 50,
    ) -> Dict[str, Any]:
        """List private archived threads that the bot has joined."""
        try:
            channel = client.get_channel(channel_id)
            if not channel:
                return {"success": False, "error": f"Channel {channel_id} not found"}

            # Check bot permissions
            bot_member = (
                channel.guild.get_member(client.user.id) if client.user else None
            )
            if not bot_member or not bot_member.guild_permissions.view_channel:
                return {"success": False, "error": "Bot lacks view_channel permission"}

            # Get joined private archived threads
            threads = []
            async for thread in channel.archived_threads(
                joined=True, private=True, before=before, limit=limit
            ):
                thread_data = {
                    "id": str(thread.id),
                    "name": thread.name,
                    "owner_id": str(thread.owner_id) if thread.owner_id else None,
                    "parent_id": str(thread.parent_id) if thread.parent_id else None,
                    "message_count": thread.message_count,
                    "member_count": len(thread.members)
                    if hasattr(thread, "members")
                    else 0,
                    "created_at": safe_isoformat(thread.created_at),
                    "archived_at": safe_isoformat(getattr(thread, "archived_at", None)),
                    "auto_archive_duration": thread.auto_archive_duration,
                    "locked": thread.locked,
                    "type": str(thread.type),
                }
                threads.append(thread_data)

            return {
                "success": True,
                "data": {
                    "channel_id": str(channel_id),
                    "threads": threads,
                    "count": len(threads),
                    "has_more": len(threads) == limit if limit else False,
                },
            }

        except ValueError:
            return {"success": False, "error": "Invalid channel ID format"}
        except discord.HTTPException as e:
            return {"success": False, "error": f"Discord API error: {e}"}
        except Exception as e:
            logger.error(f"Error listing joined private archived threads: {e}")
            return {"success": False, "error": f"Unexpected error: {e}"}

    # Log tool registration
    logger.info("Registered 15 Discord forum management tools")
