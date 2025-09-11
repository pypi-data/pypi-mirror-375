"""Discord content management FastMCP tools."""

from typing import Any, Dict, Optional, List
import discord
from loguru import logger

try:
    from fastmcp import FastMCP
except ImportError:
    logger.error("FastMCP not installed. Please run: uv add fastmcp>=2.12.0")
    raise


def register_content_tools(app: FastMCP, client: discord.Client, config: Any) -> None:
    """Register Discord content management tools with FastMCP app."""

    @app.tool()
    async def discord_create_emoji(
        guildId: str,
        name: str,
        image: str,
        roles: Optional[List[str]] = None,
        reason: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Creates a new emoji for the server."""
        try:
            guild = client.get_guild(int(guildId))
            if not guild:
                return {
                    "success": False,
                    "error": f"Guild {guildId} not found or bot not in guild",
                }

            # Check bot permissions
            if not client.user:
                return {"success": False, "error": "Client user not available"}

            bot_member = guild.get_member(client.user.id)
            if not bot_member or not bot_member.guild_permissions.manage_emojis:
                return {
                    "success": False,
                    "error": "Bot lacks manage_emojis permission",
                }

            # Prepare roles list
            role_objects: List[discord.Role] = []
            if roles:
                for role_id in roles:
                    role = guild.get_role(int(role_id))
                    if role:
                        role_objects.append(role)

            # Convert image string to bytes (assuming base64)
            import base64

            try:
                image_bytes = base64.b64decode(image)
            except Exception:
                return {"success": False, "error": "Image must be base64 encoded"}

            # Create emoji
            emoji = await guild.create_custom_emoji(
                name=name,
                image=image_bytes,
                roles=role_objects,
                reason=reason or "Created via Discord MCP",
            )

            return {
                "success": True,
                "data": {
                    "emoji_id": str(emoji.id),
                    "name": emoji.name,
                    "url": str(emoji.url),
                    "guild_id": str(guildId),
                    "animated": emoji.animated,
                    "managed": emoji.managed,
                    "available": emoji.available,
                },
            }

        except ValueError:
            return {"success": False, "error": "Invalid guild ID or role ID format"}
        except discord.Forbidden:
            return {"success": False, "error": "Bot lacks permission to manage emojis"}
        except discord.HTTPException as e:
            return {"success": False, "error": f"Discord API error: {e}"}
        except Exception as e:
            logger.error(f"Error creating emoji: {e}")
            return {"success": False, "error": f"Unexpected error: {e}"}

    @app.tool()
    async def discord_delete_emoji(
        guildId: str, emojiId: str, reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """Deletes an emoji from the server."""
        try:
            guild = client.get_guild(int(guildId))
            if not guild:
                return {
                    "success": False,
                    "error": f"Guild {guildId} not found or bot not in guild",
                }

            # Get emoji
            emoji = discord.utils.get(guild.emojis, id=int(emojiId))
            if not emoji:
                return {"success": False, "error": f"Emoji {emojiId} not found"}

            # Check bot permissions
            if not client.user:
                return {"success": False, "error": "Client user not available"}

            bot_member = guild.get_member(client.user.id)
            if not bot_member or not bot_member.guild_permissions.manage_emojis:
                return {
                    "success": False,
                    "error": "Bot lacks manage_emojis permission",
                }

            emoji_name = emoji.name
            await emoji.delete(reason=reason or "Deleted via Discord MCP")

            return {
                "success": True,
                "data": {
                    "deleted_emoji_id": emojiId,
                    "deleted_emoji_name": emoji_name,
                    "guild_id": str(guildId),
                },
            }

        except ValueError:
            return {"success": False, "error": "Invalid guild ID or emoji ID format"}
        except discord.Forbidden:
            return {"success": False, "error": "Bot lacks permission to manage emojis"}
        except discord.HTTPException as e:
            return {"success": False, "error": f"Discord API error: {e}"}
        except Exception as e:
            logger.error(f"Error deleting emoji: {e}")
            return {"success": False, "error": f"Unexpected error: {e}"}

    @app.tool()
    async def discord_list_emojis(guildId: str) -> Dict[str, Any]:
        """Lists all emojis in the server."""
        try:
            guild = client.get_guild(int(guildId))
            if not guild:
                return {
                    "success": False,
                    "error": f"Guild {guildId} not found or bot not in guild",
                }

            # Check bot permissions
            if not client.user:
                return {"success": False, "error": "Client user not available"}

            bot_member = guild.get_member(client.user.id)
            if not bot_member or not bot_member.guild_permissions.view_channel:
                return {"success": False, "error": "Bot lacks view_channel permission"}

            emojis = []
            for emoji in guild.emojis:
                emoji_data = {
                    "id": str(emoji.id),
                    "name": emoji.name,
                    "url": str(emoji.url),
                    "animated": emoji.animated,
                    "managed": emoji.managed,
                    "available": emoji.available,
                    "created_at": emoji.created_at.isoformat()
                    if emoji.created_at
                    else None,
                    "user_id": str(emoji.user.id) if emoji.user else None,
                }
                emojis.append(emoji_data)

            return {
                "success": True,
                "data": {
                    "guild_id": str(guildId),
                    "emojis": emojis,
                    "total_count": len(emojis),
                },
            }

        except ValueError:
            return {"success": False, "error": "Invalid guild ID format"}
        except discord.Forbidden:
            return {"success": False, "error": "Bot lacks permission to view emojis"}
        except discord.HTTPException as e:
            return {"success": False, "error": f"Discord API error: {e}"}
        except Exception as e:
            logger.error(f"Error listing emojis: {e}")
            return {"success": False, "error": f"Unexpected error: {e}"}

    @app.tool()
    async def discord_create_sticker(
        guildId: str,
        name: str,
        description: str,
        tags: str,
        file: str,
        reason: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Creates a new sticker for the server."""
        try:
            guild = client.get_guild(int(guildId))
            if not guild:
                return {
                    "success": False,
                    "error": f"Guild {guildId} not found or bot not in guild",
                }

            # Check bot permissions
            if not client.user:
                return {"success": False, "error": "Client user not available"}

            bot_member = guild.get_member(client.user.id)
            if not bot_member or not bot_member.guild_permissions.manage_emojis:
                return {
                    "success": False,
                    "error": "Bot lacks manage_emojis permission",
                }

            # For now, return not implemented as sticker creation requires File objects
            return {
                "success": False,
                "error": "Sticker creation requires File object handling - not yet implemented",
                "note": "This feature requires proper file upload handling",
            }

        except ValueError:
            return {"success": False, "error": "Invalid guild ID format"}
        except discord.Forbidden:
            return {
                "success": False,
                "error": "Bot lacks permission to manage stickers",
            }
        except discord.HTTPException as e:
            return {"success": False, "error": f"Discord API error: {e}"}
        except Exception as e:
            logger.error(f"Error creating sticker: {e}")
            return {"success": False, "error": f"Unexpected error: {e}"}

    @app.tool()
    async def discord_delete_sticker(
        guildId: str, stickerId: str, reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """Deletes a sticker from the server."""
        try:
            guild = client.get_guild(int(guildId))
            if not guild:
                return {
                    "success": False,
                    "error": f"Guild {guildId} not found or bot not in guild",
                }

            # Get sticker
            sticker = discord.utils.get(guild.stickers, id=int(stickerId))
            if not sticker:
                return {"success": False, "error": f"Sticker {stickerId} not found"}

            # Check bot permissions
            if not client.user:
                return {"success": False, "error": "Client user not available"}

            bot_member = guild.get_member(client.user.id)
            if not bot_member or not bot_member.guild_permissions.manage_emojis:
                return {
                    "success": False,
                    "error": "Bot lacks manage_emojis permission",
                }

            sticker_name = sticker.name
            await sticker.delete(reason=reason or "Deleted via Discord MCP")

            return {
                "success": True,
                "data": {
                    "deleted_sticker_id": stickerId,
                    "deleted_sticker_name": sticker_name,
                    "guild_id": str(guildId),
                },
            }

        except ValueError:
            return {"success": False, "error": "Invalid guild ID or sticker ID format"}
        except discord.Forbidden:
            return {
                "success": False,
                "error": "Bot lacks permission to manage stickers",
            }
        except discord.HTTPException as e:
            return {"success": False, "error": f"Discord API error: {e}"}
        except Exception as e:
            logger.error(f"Error deleting sticker: {e}")
            return {"success": False, "error": f"Unexpected error: {e}"}

    @app.tool()
    async def discord_list_stickers(guildId: str) -> Dict[str, Any]:
        """Lists all stickers in the server."""
        try:
            guild = client.get_guild(int(guildId))
            if not guild:
                return {
                    "success": False,
                    "error": f"Guild {guildId} not found or bot not in guild",
                }

            # Check bot permissions
            if not client.user:
                return {"success": False, "error": "Client user not available"}

            bot_member = guild.get_member(client.user.id)
            if not bot_member or not bot_member.guild_permissions.view_channel:
                return {"success": False, "error": "Bot lacks view_channel permission"}

            stickers = []
            for sticker in guild.stickers:
                sticker_data = {
                    "id": str(sticker.id),
                    "name": sticker.name,
                    "description": sticker.description,
                    "tags": sticker.emoji,
                    "format_type": str(sticker.format),
                    "available": sticker.available,
                    "created_at": sticker.created_at.isoformat()
                    if sticker.created_at
                    else None,
                    "user_id": str(sticker.user.id) if sticker.user else None,
                }
                stickers.append(sticker_data)

            return {
                "success": True,
                "data": {
                    "guild_id": str(guildId),
                    "stickers": stickers,
                    "total_count": len(stickers),
                },
            }

        except ValueError:
            return {"success": False, "error": "Invalid guild ID format"}
        except discord.Forbidden:
            return {"success": False, "error": "Bot lacks permission to view stickers"}
        except discord.HTTPException as e:
            return {"success": False, "error": f"Discord API error: {e}"}
        except Exception as e:
            logger.error(f"Error listing stickers: {e}")
            return {"success": False, "error": f"Unexpected error: {e}"}

    @app.tool()
    async def discord_create_invite(
        channelId: str,
        maxAge: Optional[int] = None,
        maxUses: Optional[int] = None,
        temporary: Optional[bool] = None,
        unique: Optional[bool] = None,
        targetUserId: Optional[str] = None,
        targetApplicationId: Optional[str] = None,
        reason: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Creates an invite for a channel."""
        try:
            channel = client.get_channel(int(channelId))
            if not channel:
                return {"success": False, "error": f"Channel {channelId} not found"}

            if not isinstance(channel, (discord.TextChannel, discord.VoiceChannel)):
                return {
                    "success": False,
                    "error": "Channel type does not support invites",
                }

            # Check bot permissions
            if not client.user:
                return {"success": False, "error": "Client user not available"}

            bot_member = channel.guild.get_member(client.user.id)
            if not bot_member or not bot_member.guild_permissions.create_instant_invite:
                return {
                    "success": False,
                    "error": "Bot lacks create_instant_invite permission",
                }

            # Prepare invite arguments
            invite_kwargs = {}
            if maxAge is not None:
                invite_kwargs["max_age"] = maxAge
            if maxUses is not None:
                invite_kwargs["max_uses"] = maxUses
            if temporary is not None:
                invite_kwargs["temporary"] = temporary
            if unique is not None:
                invite_kwargs["unique"] = unique
            if targetUserId is not None:
                target_user = client.get_user(int(targetUserId))
                if target_user:
                    invite_kwargs["target_user"] = target_user
            if targetApplicationId is not None:
                invite_kwargs["target_application_id"] = int(targetApplicationId)
            if reason:
                invite_kwargs["reason"] = reason

            # Create invite
            invite = await channel.create_invite(**invite_kwargs)

            return {
                "success": True,
                "data": {
                    "invite_code": invite.code,
                    "url": invite.url,
                    "channel_id": str(channelId),
                    "guild_id": str(channel.guild.id),
                    "max_age": invite.max_age,
                    "max_uses": invite.max_uses,
                    "temporary": invite.temporary,
                    "created_at": invite.created_at.isoformat()
                    if invite.created_at
                    else None,
                    "expires_at": invite.expires_at.isoformat()
                    if invite.expires_at
                    else None,
                },
            }

        except ValueError:
            return {"success": False, "error": "Invalid channel ID or user ID format"}
        except discord.Forbidden:
            return {"success": False, "error": "Bot lacks permission to create invites"}
        except discord.HTTPException as e:
            return {"success": False, "error": f"Discord API error: {e}"}
        except Exception as e:
            logger.error(f"Error creating invite: {e}")
            return {"success": False, "error": f"Unexpected error: {e}"}

    @app.tool()
    async def discord_delete_invite(
        inviteCode: str, reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """Deletes an invite by code."""
        try:
            # Get invite
            invite = await client.fetch_invite(inviteCode)

            # Check bot permissions
            if not client.user:
                return {"success": False, "error": "Client user not available"}

            if not invite.guild:
                return {"success": False, "error": "Invite guild not available"}

            # Get guild from invite and check permissions
            guild = client.get_guild(invite.guild.id)
            if not guild:
                return {"success": False, "error": "Cannot access invite guild"}

            bot_member = guild.get_member(client.user.id)
            if not bot_member or not bot_member.guild_permissions.manage_channels:
                return {
                    "success": False,
                    "error": "Bot lacks manage_channels permission",
                }

            await invite.delete(reason=reason or "Deleted via Discord MCP")

            return {
                "success": True,
                "data": {
                    "deleted_invite_code": inviteCode,
                    "channel_id": str(invite.channel.id) if invite.channel else None,
                    "guild_id": str(invite.guild.id) if invite.guild else None,
                },
            }

        except ValueError:
            return {"success": False, "error": "Invalid invite code format"}
        except discord.NotFound:
            return {"success": False, "error": "Invite not found"}
        except discord.Forbidden:
            return {"success": False, "error": "Bot lacks permission to delete invites"}
        except discord.HTTPException as e:
            return {"success": False, "error": f"Discord API error: {e}"}
        except Exception as e:
            logger.error(f"Error deleting invite: {e}")
            return {"success": False, "error": f"Unexpected error: {e}"}

    @app.tool()
    async def discord_list_invites(guildId: str) -> Dict[str, Any]:
        """Lists all invites for the server."""
        try:
            guild = client.get_guild(int(guildId))
            if not guild:
                return {
                    "success": False,
                    "error": f"Guild {guildId} not found or bot not in guild",
                }

            # Check bot permissions
            if not client.user:
                return {"success": False, "error": "Client user not available"}

            bot_member = guild.get_member(client.user.id)
            if not bot_member or not bot_member.guild_permissions.manage_guild:
                return {
                    "success": False,
                    "error": "Bot lacks manage_guild permission",
                }

            # Get all invites
            invites = await guild.invites()

            invites_data = []
            for invite in invites:
                invite_data = {
                    "code": invite.code,
                    "url": invite.url,
                    "channel_id": str(invite.channel.id) if invite.channel else None,
                    "channel_name": invite.channel.name
                    if invite.channel and hasattr(invite.channel, "name")
                    else None,
                    "max_age": invite.max_age,
                    "max_uses": invite.max_uses,
                    "uses": invite.uses,
                    "temporary": invite.temporary,
                    "created_at": invite.created_at.isoformat()
                    if invite.created_at
                    else None,
                    "expires_at": invite.expires_at.isoformat()
                    if invite.expires_at
                    else None,
                    "inviter_id": str(invite.inviter.id) if invite.inviter else None,
                    "inviter_name": invite.inviter.name if invite.inviter else None,
                }
                invites_data.append(invite_data)

            return {
                "success": True,
                "data": {
                    "guild_id": str(guildId),
                    "invites": invites_data,
                    "total_count": len(invites_data),
                },
            }

        except ValueError:
            return {"success": False, "error": "Invalid guild ID format"}
        except discord.Forbidden:
            return {"success": False, "error": "Bot lacks permission to manage invites"}
        except discord.HTTPException as e:
            return {"success": False, "error": f"Discord API error: {e}"}
        except Exception as e:
            logger.error(f"Error listing invites: {e}")
            return {"success": False, "error": f"Unexpected error: {e}"}

    @app.tool()
    async def discord_list_integrations(guildId: str) -> Dict[str, Any]:
        """Lists all integrations for the server."""
        try:
            guild = client.get_guild(int(guildId))
            if not guild:
                return {
                    "success": False,
                    "error": f"Guild {guildId} not found or bot not in guild",
                }

            # Check bot permissions
            if not client.user:
                return {"success": False, "error": "Client user not available"}

            bot_member = guild.get_member(client.user.id)
            if not bot_member or not bot_member.guild_permissions.manage_guild:
                return {
                    "success": False,
                    "error": "Bot lacks manage_guild permission",
                }

            # Get integrations
            integrations = await guild.integrations()

            integrations_data = []
            for integration in integrations:
                integration_data = {
                    "id": str(integration.id),
                    "name": integration.name,
                    "type": integration.type,
                    "enabled": integration.enabled,
                    "syncing": getattr(integration, "syncing", None),
                    "role_id": str(
                        getattr(getattr(integration, "role", None), "id", None)
                    )
                    if hasattr(integration, "role")
                    and getattr(integration, "role", None)
                    else None,
                    "enable_emoticons": getattr(integration, "enable_emoticons", None),
                    "expire_behavior": getattr(integration, "expire_behavior", None),
                    "expire_grace_period": getattr(
                        integration, "expire_grace_period", None
                    ),
                    "user_id": str(integration.user.id)
                    if hasattr(integration, "user") and integration.user
                    else None,
                    "account": {
                        "id": integration.account.id,
                        "name": integration.account.name,
                    }
                    if hasattr(integration, "account") and integration.account
                    else None,
                }
                integrations_data.append(integration_data)

            return {
                "success": True,
                "data": {
                    "guild_id": str(guildId),
                    "integrations": integrations_data,
                    "total_count": len(integrations_data),
                },
            }

        except ValueError:
            return {"success": False, "error": "Invalid guild ID format"}
        except discord.Forbidden:
            return {
                "success": False,
                "error": "Bot lacks permission to manage integrations",
            }
        except discord.HTTPException as e:
            return {"success": False, "error": f"Discord API error: {e}"}
        except Exception as e:
            logger.error(f"Error listing integrations: {e}")
            return {"success": False, "error": f"Unexpected error: {e}"}

    @app.tool()
    async def discord_delete_integration(
        guildId: str, integrationId: str, reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """Deletes an integration from the server."""
        try:
            guild = client.get_guild(int(guildId))
            if not guild:
                return {
                    "success": False,
                    "error": f"Guild {guildId} not found or bot not in guild",
                }

            # Check bot permissions
            if not client.user:
                return {"success": False, "error": "Client user not available"}

            bot_member = guild.get_member(client.user.id)
            if not bot_member or not bot_member.guild_permissions.manage_guild:
                return {
                    "success": False,
                    "error": "Bot lacks manage_guild permission",
                }

            # Get integrations and find the one to delete
            integrations = await guild.integrations()
            integration = discord.utils.get(integrations, id=int(integrationId))

            if not integration:
                return {
                    "success": False,
                    "error": f"Integration {integrationId} not found",
                }

            integration_name = integration.name
            await integration.delete(reason=reason or "Deleted via Discord MCP")

            return {
                "success": True,
                "data": {
                    "deleted_integration_id": integrationId,
                    "deleted_integration_name": integration_name,
                    "guild_id": str(guildId),
                },
            }

        except ValueError:
            return {
                "success": False,
                "error": "Invalid guild ID or integration ID format",
            }
        except discord.Forbidden:
            return {
                "success": False,
                "error": "Bot lacks permission to manage integrations",
            }
        except discord.HTTPException as e:
            return {"success": False, "error": f"Discord API error: {e}"}
        except Exception as e:
            logger.error(f"Error deleting integration: {e}")
            return {"success": False, "error": f"Unexpected error: {e}"}

    # Log content tool registration
    logger.info(
        "Registered Discord content management tools: create_emoji, delete_emoji, list_emojis, create_sticker, delete_sticker, list_stickers, create_invite, delete_invite, list_invites, list_integrations, delete_integration"
    )
