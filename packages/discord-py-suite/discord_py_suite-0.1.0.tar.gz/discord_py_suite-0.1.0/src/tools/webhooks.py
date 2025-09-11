"""Webhook management FastMCP tools."""

from typing import Any, Dict, Optional
import discord
from loguru import logger

try:
    from fastmcp import FastMCP
except ImportError:
    logger.error("FastMCP not installed. Please run: uv add fastmcp>=2.12.0")
    raise


async def _send_webhook_request(
    webhook: discord.Webhook,
    content: str,
    username: Optional[str] = None,
    avatar_url: Optional[str] = None,
) -> Dict[str, Any]:
    """Helper function to send webhook execution."""
    # Discord webhooks can be executed through the HTTP API
    # For full execution, we'd normally use requests or aiohttp directly
    # But for now, we'll use discord.py's webhook support where available
    try:
        # Send with explicitly provided parameters
        if username is not None and avatar_url is not None:
            await webhook.send(
                content=content, username=username, avatar_url=avatar_url
            )
        elif username is not None:
            await webhook.send(content=content, username=username)
        elif avatar_url is not None:
            await webhook.send(content=content, avatar_url=avatar_url)
        else:
            await webhook.send(content=content)
        return {
            "message_id": None,
            "channel_id": str(webhook.channel.id) if webhook.channel else "unknown",
        }
    except discord.HTTPException as e:
        return {"error": f"Webhook execution failed: {e}"}


def register_webhook_tools(app: FastMCP, client: discord.Client, config: Any) -> None:
    """Register webhook tools with FastMCP app."""

    @app.tool()
    async def discord_create_webhook(
        channel_id: str, name: str, avatar_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new webhook in the specified channel.

        Args:
            channel_id: The text channel ID where the webhook will be created
            name: The name for the new webhook
            avatar_url: Optional avatar URL for the webhook

        Returns:
            Success status with created webhook information
        """
        try:
            # Get channel and guild
            channel = client.get_channel(int(channel_id))
            if not isinstance(
                channel,
                (discord.TextChannel, discord.VoiceChannel, discord.ForumChannel),
            ):
                return {"success": False, "error": "Channel must be a text channel"}
            if not channel.permissions_for(channel.guild.me).manage_webhooks:
                return {
                    "success": False,
                    "error": "Bot lacks manage_webhooks permission",
                }

            # Create webhook (avatar from URL requires fetching/converting to bytes)
            webhook = await channel.create_webhook(
                name=name, reason="Created by FastMCP tool"
            )

            return {
                "success": True,
                "data": {
                    "id": str(webhook.id),
                    "url": webhook.url,
                    "token": webhook.token,
                    "name": webhook.name,
                    "channel_id": str(webhook.channel_id),
                    "guild_id": str(webhook.guild_id) if webhook.guild_id else None,
                    "avatar": webhook.avatar.url if webhook.avatar else None,
                    "user_id": str(webhook.user.id) if webhook.user else None,
                },
            }
        except discord.Forbidden:
            return {"success": False, "error": "Bot lacks required permissions"}
        except discord.NotFound:
            return {"success": False, "error": "Channel not found"}
        except discord.HTTPException as e:
            return {"success": False, "error": f"Discord API error: {e}"}
        except Exception as e:
            logger.error(f"Error in create_webhook: {e}")
            return {"success": False, "error": str(e)}

    @app.tool()
    async def discord_execute_webhook(
        webhook_id: str,
        token: str,
        content: str,
        username: Optional[str] = None,
        avatar_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Execute a webhook to send a message.

        Args:
            webhook_id: The webhook ID
            token: The webhook token (sensitive, must be kept secure)
            content: The message content to send
            username: Optional override for the webhook username
            avatar_url: Optional override for the webhook avatar

        Returns:
            Success status with execution result
        """
        try:
            webhook = discord.Webhook.partial(int(webhook_id), token, client=client)

            # Send the message with proper parameter handling
            if username is not None and avatar_url is not None:
                message = await webhook.send(
                    content=content, username=username, avatar_url=avatar_url, wait=True
                )
            elif username is not None:
                message = await webhook.send(
                    content=content, username=username, wait=True
                )
            elif avatar_url is not None:
                message = await webhook.send(
                    content=content, avatar_url=avatar_url, wait=True
                )
            else:
                message = await webhook.send(content=content, wait=True)

            return {
                "success": True,
                "data": {
                    "message_id": str(message.id),
                    "channel_id": str(message.channel.id),
                    "webhook_id": webhook_id,
                    "content_preview": content[:100] + "..."
                    if len(content) > 100
                    else content,
                    "username": username or "Webhook",
                    "timestamp": message.created_at.isoformat(),
                },
            }
        except discord.Forbidden:
            return {"success": False, "error": "Webhook execution forbidden"}
        except discord.NotFound:
            return {"success": False, "error": "Webhook or channel not found"}
        except discord.HTTPException as e:
            return {"success": False, "error": f"Discord API error: {e}"}
        except Exception as e:
            logger.error(f"Error in execute_webhook: {e}")
            return {"success": False, "error": str(e)}

    @app.tool()
    async def discord_edit_webhook(
        webhook_id: str, name: Optional[str] = None, avatar_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """Edit an existing webhook.

        Args:
            webhook_id: The webhook ID to edit
            name: Optional new name for the webhook
            avatar_url: Optional new avatar URL

        Returns:
            Success status with updated webhook information
        """
        try:
            webhook = await client.fetch_webhook(int(webhook_id))

            # Check permissions - bot must have manage_webhooks in the guild
            guild = client.get_guild(webhook.guild_id) if webhook.guild_id else None
            if guild:
                member = guild.get_member(client.user.id) if client.user else None
                if not member or not member.guild_permissions.manage_webhooks:
                    return {
                        "success": False,
                        "error": "Bot lacks manage_webhooks permission",
                    }

            # Edit webhook (avatar from URL requires fetching/converting to bytes)
            if name is not None:
                await webhook.edit(name=name, reason="Edited by FastMCP tool")
            # Note: avatar editing from URL would require fetching and converting to bytes
            # For now, skip avatar editing from URL

            return {
                "success": True,
                "data": {
                    "id": str(webhook.id),
                    "name": webhook.name,
                    "channel_id": str(webhook.channel_id),
                    "guild_id": str(webhook.guild_id) if webhook.guild_id else None,
                    "avatar": webhook.avatar.url if webhook.avatar else None,
                },
            }
        except discord.Forbidden:
            return {"success": False, "error": "Bot lacks required permissions"}
        except discord.NotFound:
            return {"success": False, "error": "Webhook not found"}
        except discord.HTTPException as e:
            return {"success": False, "error": f"Discord API error: {e}"}
        except Exception as e:
            logger.error(f"Error in edit_webhook: {e}")
            return {"success": False, "error": str(e)}

    @app.tool()
    async def discord_delete_webhook(webhook_id: str) -> Dict[str, Any]:
        """Delete an existing webhook.

        Args:
            webhook_id: The webhook ID to delete

        Returns:
            Success status with deletion confirmation
        """
        try:
            webhook = await client.fetch_webhook(int(webhook_id))

            # Check permissions
            guild = client.get_guild(webhook.guild_id) if webhook.guild_id else None
            if guild:
                member = guild.get_member(client.user.id) if client.user else None
                if not member or not member.guild_permissions.manage_webhooks:
                    return {
                        "success": False,
                        "error": "Bot lacks manage_webhooks permission",
                    }

            webhook_info = {
                "id": str(webhook.id),
                "name": webhook.name,
                "channel_id": str(webhook.channel_id),
                "guild_id": str(webhook.guild_id) if webhook.guild_id else None,
            }

            await webhook.delete(reason="Deleted by FastMCP tool")

            return {
                "success": True,
                "data": {
                    "deleted_webhook": webhook_info,
                    "message": f"Successfully deleted webhook '{webhook.name}'",
                },
            }
        except discord.Forbidden:
            return {"success": False, "error": "Bot lacks required permissions"}
        except discord.NotFound:
            return {"success": False, "error": "Webhook not found"}
        except discord.HTTPException as e:
            return {"success": False, "error": f"Discord API error: {e}"}
        except Exception as e:
            logger.error(f"Error in delete_webhook: {e}")
            return {"success": False, "error": str(e)}

    @app.tool()
    async def discord_get_webhook(
        webhook_id: str, token: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get information about a webhook.

        Args:
            webhook_id: The webhook ID to retrieve
            token: Optional webhook token (only needed for private webhooks)

        Returns:
            Success status with webhook information
        """
        try:
            if token:
                webhook = discord.Webhook.partial(int(webhook_id), token, client=client)
            else:
                webhook = await client.fetch_webhook(int(webhook_id))

            return {
                "success": True,
                "data": {
                    "id": str(webhook.id),
                    "url": webhook.url if hasattr(webhook, "url") else None,
                    "token": webhook.token if hasattr(webhook, "token") else None,
                    "name": webhook.name,
                    "channel_id": str(webhook.channel_id),
                    "guild_id": str(webhook.guild_id) if webhook.guild_id else None,
                    "avatar": webhook.avatar.url if webhook.avatar else None,
                    "user_id": str(webhook.user.id) if webhook.user else None,
                    "type": str(webhook.type),
                    "created_at": webhook.created_at.isoformat()
                    if hasattr(webhook, "created_at")
                    else None,
                },
            }
        except discord.Forbidden:
            return {"success": False, "error": "Bot lacks required permissions"}
        except discord.NotFound:
            return {"success": False, "error": "Webhook not found"}
        except discord.HTTPException as e:
            return {"success": False, "error": f"Discord API error: {e}"}
        except Exception as e:
            logger.error(f"Error in get_webhook: {e}")
            return {"success": False, "error": str(e)}

    @app.tool()
    async def discord_list_channel_webhooks(channel_id: str) -> Dict[str, Any]:
        """List all webhooks in a specific channel.

        Args:
            channel_id: The channel ID to list webhooks for

        Returns:
            Success status with list of channel webhooks
        """
        try:
            channel = client.get_channel(int(channel_id))
            if not isinstance(channel, discord.TextChannel):
                return {"success": False, "error": "Channel must be a text channel"}

            # Check permissions
            if not channel.permissions_for(channel.guild.me).manage_webhooks:
                return {
                    "success": False,
                    "error": "Bot lacks manage_webhooks permission",
                }

            webhooks = await channel.webhooks()

            webhook_list = []
            for webhook in webhooks:
                webhook_list.append(
                    {
                        "id": str(webhook.id),
                        "url": webhook.url,
                        "token": webhook.token,
                        "name": webhook.name,
                        "channel_id": str(webhook.channel_id),
                        "guild_id": str(webhook.guild_id) if webhook.guild_id else None,
                        "avatar": webhook.avatar.url if webhook.avatar else None,
                        "user_id": str(webhook.user.id) if webhook.user else None,
                        "type": str(webhook.type),
                        "created_at": webhook.created_at.isoformat(),
                    }
                )

            return {
                "success": True,
                "data": {
                    "channel": {
                        "id": str(channel.id),
                        "name": channel.name,
                        "guild_id": str(channel.guild.id),
                    },
                    "webhooks": webhook_list,
                    "total_count": len(webhook_list),
                },
            }
        except discord.Forbidden:
            return {"success": False, "error": "Bot lacks required permissions"}
        except discord.NotFound:
            return {"success": False, "error": "Channel not found"}
        except discord.HTTPException as e:
            return {"success": False, "error": f"Discord API error: {e}"}
        except Exception as e:
            logger.error(f"Error in list_channel_webhooks: {e}")
            return {"success": False, "error": str(e)}

    @app.tool()
    async def discord_list_guild_webhooks(guild_id: str) -> Dict[str, Any]:
        """List all webhooks in the entire server.

        Args:
            guild_id: The Discord server (guild) ID

        Returns:
            Success status with list of all guild webhooks
        """
        try:
            guild = client.get_guild(int(guild_id))
            if not guild:
                return {"success": False, "error": f"Guild {guild_id} not found"}

            # Check permissions
            member = guild.get_member(client.user.id) if client.user else None
            if not member or not member.guild_permissions.manage_webhooks:
                return {
                    "success": False,
                    "error": "Bot lacks manage_webhooks permission",
                }

            webhooks = await guild.webhooks()

            webhook_list = []
            for webhook in webhooks:
                webhook_list.append(
                    {
                        "id": str(webhook.id),
                        "url": webhook.url,
                        "token": webhook.token,
                        "name": webhook.name,
                        "channel_id": str(webhook.channel_id),
                        "guild_id": str(webhook.guild_id) if webhook.guild_id else None,
                        "avatar": webhook.avatar.url if webhook.avatar else None,
                        "user_id": str(webhook.user.id) if webhook.user else None,
                        "type": str(webhook.type),
                        "created_at": webhook.created_at.isoformat(),
                    }
                )

            return {
                "success": True,
                "data": {
                    "guild": {
                        "id": str(guild.id),
                        "name": guild.name,
                    },
                    "webhooks": webhook_list,
                    "total_count": len(webhook_list),
                },
            }
        except discord.Forbidden:
            return {"success": False, "error": "Bot lacks required permissions"}
        except discord.NotFound:
            return {"success": False, "error": "Guild not found"}
        except discord.HTTPException as e:
            return {"success": False, "error": f"Discord API error: {e}"}
        except Exception as e:
            logger.error(f"Error in list_guild_webhooks: {e}")
            return {"success": False, "error": str(e)}

    @app.tool()
    async def discord_test_webhook(webhook_id: str, token: str) -> Dict[str, Any]:
        """Test a webhook by sending a test message.

        Args:
            webhook_id: The webhook ID to test
            token: The webhook token

        Returns:
            Success status with test result
        """
        try:
            test_content = "🧪 Webhook Test - This is a test message from FastMCP"
            webhook = discord.Webhook.partial(int(webhook_id), token, client=client)

            # Send a test message
            message = await webhook.send(
                content=test_content,
                username="FastMCP Test Bot",
                avatar_url="https://cdn.discordapp.com/avatars/000000000000000000/example.png",
                wait=True,
            )

            return {
                "success": True,
                "data": {
                    "test_message_id": str(message.id),
                    "channel_id": str(message.channel.id),
                    "webhook_id": webhook_id,
                    "test_content": test_content,
                    "timestamp": message.created_at.isoformat(),
                    "message": "Webhook test successful! Check the channel for the test message.",
                },
            }
        except discord.Forbidden:
            return {"success": False, "error": "Webhook execution forbidden"}
        except discord.NotFound:
            return {"success": False, "error": "Webhook or channel not found"}
        except discord.HTTPException as e:
            return {"success": False, "error": f"Discord API error: {e}"}
        except Exception as e:
            logger.error(f"Error in test_webhook: {e}")
            return {"success": False, "error": str(e)}
