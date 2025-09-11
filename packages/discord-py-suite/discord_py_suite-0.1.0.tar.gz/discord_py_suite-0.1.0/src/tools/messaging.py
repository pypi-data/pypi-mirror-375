"""Discord messaging FastMCP tools."""

from typing import Any, Dict, List, Optional
import discord
from loguru import logger


try:
    from fastmcp import FastMCP
except ImportError:
    logger.error("FastMCP not installed. Please run: uv add fastmcp>=2.12.0")
    raise


def register_messaging_tools(app: FastMCP, client: discord.Client, config: Any) -> None:
    """Register Discord messaging tools with FastMCP app."""

    @app.tool()
    async def discord_send_message(
        channel_id: str,
        content: str,
        embed_title: Optional[str] = None,
        embed_description: Optional[str] = None,
        embed_color: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Send a message to a Discord channel.

        Args:
            channel_id: The Discord channel ID to send the message to
            content: The text content of the message
            embed_title: Optional embed title
            embed_description: Optional embed description
            embed_color: Optional embed color (as integer)

        Returns:
            Success status and message information
        """
        try:
            channel = client.get_channel(int(channel_id))
            if not channel:
                return {
                    "success": False,
                    "error": f"Channel {channel_id} not found or bot lacks access",
                }

            # Ensure channel supports sending messages
            if not isinstance(
                channel,
                (
                    discord.TextChannel,
                    discord.DMChannel,
                    discord.GroupChannel,
                    discord.Thread,
                ),
            ):
                return {
                    "success": False,
                    "error": "Channel type does not support sending messages",
                }

            # Check permissions for guild channels
            if isinstance(channel, discord.abc.GuildChannel):
                bot_member = (
                    channel.guild.get_member(client.user.id) if client.user else None
                )
                if (
                    not bot_member
                    or not channel.permissions_for(bot_member).send_messages
                ):
                    return {
                        "success": False,
                        "error": "Bot lacks send_messages permission in this channel",
                    }

            # Create embed if specified
            embed = None
            if embed_title or embed_description:
                embed = discord.Embed(
                    title=embed_title,
                    description=embed_description,
                    color=embed_color or 0x3498DB,
                )

            # Send message
            if embed:
                message = await channel.send(content=content, embed=embed)
            else:
                message = await channel.send(content=content)

            return {
                "success": True,
                "data": {
                    "message_id": str(message.id),
                    "channel_id": str(message.channel.id),
                    "content": message.content,
                    "created_at": message.created_at.isoformat(),
                },
            }

        except ValueError:
            return {"success": False, "error": "Invalid channel ID format"}
        except discord.Forbidden:
            return {"success": False, "error": "Bot lacks required permissions"}
        except discord.NotFound:
            return {"success": False, "error": "Channel not found"}
        except discord.HTTPException as e:
            return {"success": False, "error": f"Discord API error: {e}"}
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return {"success": False, "error": f"Unexpected error: {e}"}

    @app.tool()
    async def discord_get_messages(
        channel_id: str,
        limit: int = 10,
        before: Optional[str] = None,
        after: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get messages from a Discord channel.

        Args:
            channel_id: The Discord channel ID to get messages from
            limit: Maximum number of messages to retrieve (1-100, default 10)
            before: Get messages before this message ID
            after: Get messages after this message ID

        Returns:
            List of messages with their information
        """
        try:
            # Validate limit
            if not 1 <= limit <= 100:
                return {"success": False, "error": "Limit must be between 1 and 100"}

            channel = client.get_channel(int(channel_id))
            if not channel:
                return {
                    "success": False,
                    "error": f"Channel {channel_id} not found or bot lacks access",
                }

            # Ensure channel supports message history
            if not isinstance(
                channel,
                (
                    discord.TextChannel,
                    discord.DMChannel,
                    discord.GroupChannel,
                    discord.Thread,
                ),
            ):
                return {
                    "success": False,
                    "error": "Channel type does not support message history",
                }

            # Check permissions for guild channels
            if isinstance(channel, discord.abc.GuildChannel):
                bot_member = (
                    channel.guild.get_member(client.user.id) if client.user else None
                )
                if (
                    not bot_member
                    or not channel.permissions_for(bot_member).read_messages
                ):
                    return {
                        "success": False,
                        "error": "Bot lacks read_messages permission in this channel",
                    }

            # Parse before/after parameters
            before_obj = None
            after_obj = None

            if before:
                before_obj = discord.Object(id=int(before))
            if after:
                after_obj = discord.Object(id=int(after))

            # Get messages
            messages = []
            async for message in channel.history(
                limit=limit, before=before_obj, after=after_obj
            ):
                messages.append(
                    {
                        "id": str(message.id),
                        "content": message.content,
                        "author": {
                            "id": str(message.author.id),
                            "username": message.author.name,
                            "display_name": message.author.display_name,
                            "bot": message.author.bot,
                        },
                        "created_at": message.created_at.isoformat(),
                        "edited_at": message.edited_at.isoformat()
                        if message.edited_at
                        else None,
                        "pinned": message.pinned,
                        "attachments": [
                            {
                                "id": str(attachment.id),
                                "filename": attachment.filename,
                                "size": attachment.size,
                                "url": attachment.url,
                                "content_type": attachment.content_type,
                            }
                            for attachment in message.attachments
                        ],
                    }
                )

            return {
                "success": True,
                "data": {"messages": messages, "count": len(messages)},
            }

        except ValueError:
            return {
                "success": False,
                "error": "Invalid channel ID or message ID format",
            }
        except discord.Forbidden:
            return {"success": False, "error": "Bot lacks required permissions"}
        except discord.NotFound:
            return {"success": False, "error": "Channel or message not found"}
        except discord.HTTPException as e:
            return {"success": False, "error": f"Discord API error: {e}"}
        except Exception as e:
            logger.error(f"Error getting messages: {e}")
            return {"success": False, "error": f"Unexpected error: {e}"}

    @app.tool()
    async def discord_edit_message(
        channel_id: str, message_id: str, content: str
    ) -> Dict[str, Any]:
        """Edit an existing Discord message sent by the bot.

        Args:
            channel_id: The Discord channel ID containing the message
            message_id: The ID of the message to edit
            content: The new message content

        Returns:
            Success status and updated message information
        """
        try:
            channel = client.get_channel(int(channel_id))
            if not channel:
                return {
                    "success": False,
                    "error": f"Channel {channel_id} not found or bot lacks access",
                }

            # Ensure channel supports messages
            if not isinstance(
                channel,
                (
                    discord.TextChannel,
                    discord.DMChannel,
                    discord.GroupChannel,
                    discord.Thread,
                ),
            ):
                return {
                    "success": False,
                    "error": "Channel type does not support messages",
                }

            # Get message
            message = await channel.fetch_message(int(message_id))

            # Check if bot can edit this message
            if not client.user or message.author.id != client.user.id:
                return {"success": False, "error": "Bot can only edit its own messages"}

            # Edit message
            await message.edit(content=content)

            return {
                "success": True,
                "data": {
                    "message_id": str(message.id),
                    "channel_id": str(message.channel.id),
                    "new_content": content,
                    "edited_at": message.edited_at.isoformat()
                    if message.edited_at
                    else None,
                },
            }

        except ValueError:
            return {
                "success": False,
                "error": "Invalid channel ID or message ID format",
            }
        except discord.NotFound:
            return {"success": False, "error": "Message not found"}
        except discord.Forbidden:
            return {
                "success": False,
                "error": "Bot lacks permission to edit this message",
            }
        except discord.HTTPException as e:
            return {"success": False, "error": f"Discord API error: {e}"}
        except Exception as e:
            logger.error(f"Error editing message: {e}")
            return {"success": False, "error": f"Unexpected error: {e}"}

    @app.tool()
    async def discord_delete_message(
        channel_id: str, message_id: str
    ) -> Dict[str, Any]:
        """Delete a Discord message.

        Args:
            channel_id: The Discord channel ID containing the message
            message_id: The ID of the message to delete

        Returns:
            Success status and confirmation of deletion
        """
        try:
            channel = client.get_channel(int(channel_id))
            if not channel:
                return {
                    "success": False,
                    "error": f"Channel {channel_id} not found or bot lacks access",
                }

            # Check permissions for managing messages
            if isinstance(channel, discord.abc.GuildChannel):
                bot_member = (
                    channel.guild.get_member(client.user.id) if client.user else None
                )
                if (
                    not bot_member
                    or not channel.permissions_for(bot_member).manage_messages
                ):
                    return {
                        "success": False,
                        "error": "Bot lacks manage_messages permission in this channel",
                    }

            # Get and delete message - only supported on text-based channels
            if not isinstance(
                channel,
                (
                    discord.TextChannel,
                    discord.DMChannel,
                    discord.GroupChannel,
                    discord.Thread,
                ),
            ):
                return {
                    "success": False,
                    "error": "Channel type does not support message fetching",
                }

            message = await channel.fetch_message(int(message_id))
            await message.delete()

            return {
                "success": True,
                "data": {
                    "message": "Message deleted successfully",
                    "deleted_message_id": message_id,
                    "channel_id": channel_id,
                },
            }

        except ValueError:
            return {
                "success": False,
                "error": "Invalid channel ID or message ID format",
            }
        except discord.NotFound:
            return {"success": False, "error": "Message not found"}
        except discord.Forbidden:
            return {
                "success": False,
                "error": "Bot lacks permission to delete this message",
            }
        except discord.HTTPException as e:
            return {"success": False, "error": f"Discord API error: {e}"}
        except Exception as e:
            logger.error(f"Error deleting message: {e}")
            return {"success": False, "error": f"Unexpected error: {e}"}

    @app.tool()
    async def discord_add_reaction(
        channel_id: str, message_id: str, emoji: str
    ) -> Dict[str, Any]:
        """Add a reaction to a Discord message.

        Args:
            channel_id: The Discord channel ID containing the message
            message_id: The ID of the message to react to
            emoji: The emoji to react with (Unicode emoji or custom emoji)

        Returns:
            Success status and reaction information
        """
        try:
            channel = client.get_channel(int(channel_id))
            if not channel:
                return {
                    "success": False,
                    "error": f"Channel {channel_id} not found or bot lacks access",
                }

            # Check permissions
            if isinstance(channel, discord.abc.GuildChannel):
                bot_member = (
                    channel.guild.get_member(client.user.id) if client.user else None
                )
                if (
                    not bot_member
                    or not channel.permissions_for(bot_member).add_reactions
                ):
                    return {
                        "success": False,
                        "error": "Bot lacks add_reactions permission in this channel",
                    }

            # Check if channel supports fetch_message
            if not isinstance(
                channel,
                (
                    discord.TextChannel,
                    discord.DMChannel,
                    discord.GroupChannel,
                    discord.Thread,
                    discord.VoiceChannel,
                    discord.StageChannel,
                ),
            ):
                return {
                    "success": False,
                    "error": "Channel type does not support message reactions",
                }

            # Get message and add reaction - type narrowing for fetch_message
            if not hasattr(channel, "fetch_message"):
                return {
                    "success": False,
                    "error": "Channel type does not support message fetching",
                }
            message = await channel.fetch_message(int(message_id))
            await message.add_reaction(emoji)

            return {
                "success": True,
                "data": {
                    "message": f"Added reaction {emoji} to message",
                    "emoji": emoji,
                    "message_id": message_id,
                    "channel_id": channel_id,
                },
            }

        except ValueError:
            return {
                "success": False,
                "error": "Invalid channel ID or message ID format",
            }
        except discord.NotFound:
            return {"success": False, "error": "Message not found"}
        except discord.Forbidden:
            return {"success": False, "error": "Bot lacks permission to add reactions"}
        except discord.HTTPException as e:
            if "Unknown Emoji" in str(e):
                return {"success": False, "error": f"Invalid emoji: {emoji}"}
            return {"success": False, "error": f"Discord API error: {e}"}
        except Exception as e:
            logger.error(f"Error adding reaction: {e}")
            return {"success": False, "error": f"Unexpected error: {e}"}

    @app.tool()
    async def discord_send(channelId: str, message: str) -> Dict[str, Any]:
        """Send a message to a specified Discord text channel - simplified version."""
        try:
            # Call the existing discord_send_message function directly
            channel = client.get_channel(int(channelId))
            if not channel:
                return {
                    "success": False,
                    "error": f"Channel {channelId} not found or bot lacks access",
                }

            # Ensure channel supports sending messages
            if not isinstance(
                channel,
                (
                    discord.TextChannel,
                    discord.DMChannel,
                    discord.GroupChannel,
                    discord.Thread,
                ),
            ):
                return {
                    "success": False,
                    "error": "Channel type does not support sending messages",
                }

            # Check permissions for guild channels
            if isinstance(channel, discord.abc.GuildChannel):
                bot_member = (
                    channel.guild.get_member(client.user.id) if client.user else None
                )
                if (
                    not bot_member
                    or not channel.permissions_for(bot_member).send_messages
                ):
                    return {
                        "success": False,
                        "error": "Bot lacks send_messages permission in this channel",
                    }

            # Send message
            sent_message = await channel.send(content=message)

            return {
                "success": True,
                "data": {
                    "message_id": str(sent_message.id),
                    "channel_id": str(sent_message.channel.id),
                    "content": sent_message.content,
                    "created_at": sent_message.created_at.isoformat(),
                },
            }
        except Exception as e:
            logger.error(f"Error in discord_send: {e}")
            return {"success": False, "error": f"Failed to send message: {str(e)}"}

    @app.tool()
    async def discord_read_messages(channelId: str, limit: int = 50) -> Dict[str, Any]:
        """Read messages from a Discord channel - simplified version."""
        try:
            # Validate limit
            if not 1 <= limit <= 100:
                limit = min(max(limit, 1), 100)  # Clamp to valid range

            channel = client.get_channel(int(channelId))
            if not channel:
                return {
                    "success": False,
                    "error": f"Channel {channelId} not found or bot lacks access",
                }

            # Ensure channel supports message history
            if not isinstance(
                channel,
                (
                    discord.TextChannel,
                    discord.DMChannel,
                    discord.GroupChannel,
                    discord.Thread,
                ),
            ):
                return {
                    "success": False,
                    "error": "Channel type does not support message history",
                }

            # Check permissions for guild channels
            if isinstance(channel, discord.abc.GuildChannel):
                bot_member = (
                    channel.guild.get_member(client.user.id) if client.user else None
                )
                if (
                    not bot_member
                    or not channel.permissions_for(bot_member).read_messages
                ):
                    return {
                        "success": False,
                        "error": "Bot lacks read_messages permission in this channel",
                    }

            # Get messages
            messages = []
            async for msg in channel.history(limit=limit):
                messages.append(
                    {
                        "id": str(msg.id),
                        "content": msg.content,
                        "author": {
                            "id": str(msg.author.id),
                            "username": msg.author.name,
                            "display_name": msg.author.display_name,
                            "bot": msg.author.bot,
                        },
                        "created_at": msg.created_at.isoformat(),
                        "edited_at": msg.edited_at.isoformat()
                        if msg.edited_at
                        else None,
                        "pinned": msg.pinned,
                    }
                )

            return {
                "success": True,
                "data": {"messages": messages, "count": len(messages)},
            }
        except Exception as e:
            logger.error(f"Error in discord_read_messages: {e}")
            return {"success": False, "error": f"Failed to read messages: {str(e)}"}

    @app.tool()
    async def discord_add_multiple_reactions(
        channelId: str, messageId: str, emojis: List[str]
    ) -> Dict[str, Any]:
        """Add multiple emoji reactions to a Discord message at once."""
        try:
            if not emojis:
                return {"success": False, "error": "No emojis provided"}

            channel = client.get_channel(int(channelId))
            if not channel:
                return {
                    "success": False,
                    "error": f"Channel {channelId} not found or bot lacks access",
                }

            # Check permissions
            if isinstance(channel, discord.abc.GuildChannel):
                bot_member = (
                    channel.guild.get_member(client.user.id) if client.user else None
                )
                if (
                    not bot_member
                    or not channel.permissions_for(bot_member).add_reactions
                ):
                    return {
                        "success": False,
                        "error": "Bot lacks add_reactions permission in this channel",
                    }

            # Get message - ensure it's a messageable channel
            if not isinstance(
                channel, (discord.TextChannel, discord.DMChannel, discord.Thread)
            ):
                return {
                    "success": False,
                    "error": "Channel type does not support message fetching",
                }

            message = await channel.fetch_message(int(messageId))

            # Add reactions sequentially
            successful_reactions = []
            failed_reactions = []

            for emoji in emojis:
                try:
                    await message.add_reaction(emoji)
                    successful_reactions.append(emoji)
                except Exception as e:
                    failed_reactions.append({"emoji": emoji, "error": str(e)})

            return {
                "success": True,
                "data": {
                    "message_id": messageId,
                    "channel_id": channelId,
                    "successful_reactions": successful_reactions,
                    "failed_reactions": failed_reactions,
                    "total_attempted": len(emojis),
                    "total_successful": len(successful_reactions),
                },
            }

        except ValueError:
            return {
                "success": False,
                "error": "Invalid channel ID or message ID format",
            }
        except discord.NotFound:
            return {"success": False, "error": "Message not found"}
        except discord.Forbidden:
            return {"success": False, "error": "Bot lacks permission to add reactions"}
        except Exception as e:
            logger.error(f"Error adding multiple reactions: {e}")
            return {"success": False, "error": f"Unexpected error: {e}"}

    @app.tool()
    async def discord_remove_reaction(
        channelId: str, messageId: str, emoji: str, userId: Optional[str] = None
    ) -> Dict[str, Any]:
        """Remove a specific emoji reaction from a Discord message."""
        try:
            channel = client.get_channel(int(channelId))
            if not channel:
                return {
                    "success": False,
                    "error": f"Channel {channelId} not found or bot lacks access",
                }

            # Check permissions
            if isinstance(channel, discord.abc.GuildChannel):
                if not client.user:
                    return {"success": False, "error": "Client user not available"}

                bot_member = channel.guild.get_member(client.user.id)
                if not bot_member:
                    return {"success": False, "error": "Bot not found in guild"}

                # Check if removing own reaction or managing messages
                perms = channel.permissions_for(bot_member)
                if userId and userId != str(client.user.id):
                    if not perms.manage_messages:
                        return {
                            "success": False,
                            "error": "Bot lacks manage_messages permission to remove others' reactions",
                        }

            # Get message - ensure it's a messageable channel
            if not isinstance(
                channel, (discord.TextChannel, discord.DMChannel, discord.Thread)
            ):
                return {
                    "success": False,
                    "error": "Channel type does not support message fetching",
                }

            message = await channel.fetch_message(int(messageId))

            # Remove reaction
            if userId:
                user = client.get_user(int(userId)) or discord.Object(id=int(userId))
                await message.remove_reaction(emoji, user)
            else:
                # Remove bot's own reaction
                if client.user:
                    await message.remove_reaction(emoji, client.user)
                else:
                    return {"success": False, "error": "Client user not available"}

            return {
                "success": True,
                "data": {
                    "message": f"Removed reaction {emoji} from message",
                    "emoji": emoji,
                    "message_id": messageId,
                    "channel_id": channelId,
                    "user_id": userId
                    or (str(client.user.id) if client.user else "unknown"),
                },
            }

        except ValueError:
            return {
                "success": False,
                "error": "Invalid channel ID, message ID, or user ID format",
            }
        except discord.NotFound:
            return {"success": False, "error": "Message, user, or reaction not found"}
        except discord.Forbidden:
            return {
                "success": False,
                "error": "Bot lacks permission to remove reactions",
            }
        except Exception as e:
            logger.error(f"Error removing reaction: {e}")
            return {"success": False, "error": f"Unexpected error: {e}"}

    # Log messaging tool registration
    logger.info(
        "Registered Discord messaging tools: send_message, get_messages, edit_message, delete_message, add_reaction, send, read_messages, add_multiple_reactions, remove_reaction"
    )
