"""Discord moderation FastMCP tools."""

from typing import Any, Dict, Optional
import discord
from loguru import logger
import aiohttp

try:
    from fastmcp import FastMCP
except ImportError:
    logger.error("FastMCP not installed. Please run: uv add fastmcp>=2.12.0")
    raise


def register_moderation_tools(
    app: FastMCP, client: discord.Client, config: Any
) -> None:
    """Register Discord moderation tools with FastMCP app."""

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

    @app.tool()
    async def discord_kick_member(
        guild_id: str, user_id: str, reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """Kick a member from a Discord guild."""
        try:
            guild = client.get_guild(int(guild_id))
            if not guild:
                return {
                    "success": False,
                    "error": f"Guild {guild_id} not found or bot not in guild",
                }

            # Check bot permissions
            bot_member = guild.get_member(client.user.id) if client.user else None
            if not bot_member or not bot_member.guild_permissions.kick_members:
                return {"success": False, "error": "Bot lacks kick_members permission"}

            # Get member to kick
            member = await guild.fetch_member(int(user_id))
            if not member:
                return {
                    "success": False,
                    "error": f"Member {user_id} not found in guild",
                }

            # Check hierarchy (bot's role must be higher than target)
            if bot_member.top_role <= member.top_role:
                return {
                    "success": False,
                    "error": "Bot's role is not high enough to kick this member",
                }

            # Check if target is guild owner
            if member.id == guild.owner_id:
                return {"success": False, "error": "Cannot kick the guild owner"}

            # Store member info before kick
            member_info = {
                "id": str(member.id),
                "username": member.name,
                "display_name": member.display_name,
                "nickname": member.nick,
                "joined_at": member.joined_at.isoformat() if member.joined_at else None,
            }

            # Kick member
            await member.kick(reason=reason)

            return {
                "success": True,
                "data": {
                    "message": f"Successfully kicked {member.display_name}",
                    "kicked_member": member_info,
                    "reason": reason,
                    "guild_name": guild.name,
                },
            }

        except ValueError:
            return {"success": False, "error": "Invalid guild ID or user ID format"}
        except discord.NotFound:
            return {"success": False, "error": "Guild or member not found"}
        except discord.Forbidden:
            return {"success": False, "error": "Bot lacks permission to kick members"}
        except discord.HTTPException as e:
            return {"success": False, "error": f"Discord API error: {e}"}
        except Exception as e:
            logger.error(f"Error kicking member: {e}")
            return {"success": False, "error": f"Unexpected error: {e}"}

    @app.tool()
    async def discord_ban_member(
        guild_id: str,
        user_id: str,
        reason: Optional[str] = None,
        delete_message_days: int = 0,
    ) -> Dict[str, Any]:
        """Ban a member from a Discord guild."""
        try:
            guild = client.get_guild(int(guild_id))
            if not guild:
                return {
                    "success": False,
                    "error": f"Guild {guild_id} not found or bot not in guild",
                }

            # Check bot permissions
            bot_member = guild.get_member(client.user.id) if client.user else None
            if not bot_member or not bot_member.guild_permissions.ban_members:
                return {"success": False, "error": "Bot lacks ban_members permission"}

            # Validate delete_message_days
            if not 0 <= delete_message_days <= 7:
                return {
                    "success": False,
                    "error": "delete_message_days must be between 0 and 7",
                }

            # Ban user
            await guild.ban(
                discord.Object(id=int(user_id)),
                reason=reason,
            )

            return {
                "success": True,
                "data": {
                    "message": f"Successfully banned user {user_id}",
                    "banned_user_id": user_id,
                    "reason": reason,
                    "deleted_message_days": delete_message_days,
                    "guild_name": guild.name,
                },
            }

        except ValueError:
            return {"success": False, "error": "Invalid guild ID or user ID format"}
        except discord.Forbidden:
            return {"success": False, "error": "Bot lacks permission to ban members"}
        except discord.HTTPException as e:
            return {"success": False, "error": f"Discord API error: {e}"}
        except Exception as e:
            logger.error(f"Error banning member: {e}")
            return {"success": False, "error": f"Unexpected error: {e}"}

    @app.tool()
    async def discord_unban_member(
        guildId: str, userId: str, reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """Unbans a user from the Discord server."""
        try:
            guild = client.get_guild(int(guildId))
            if not guild:
                return {
                    "success": False,
                    "error": f"Guild {guildId} not found or bot not in guild",
                }

            # Check bot permissions
            bot_member = guild.get_member(client.user.id) if client.user else None
            if not bot_member or not bot_member.guild_permissions.ban_members:
                return {"success": False, "error": "Bot lacks ban_members permission"}

            # Unban user
            user = discord.Object(id=int(userId))
            await guild.unban(user, reason=reason or "Unbanned via Discord MCP")

            return {
                "success": True,
                "data": {
                    "message": f"Successfully unbanned user {userId}",
                    "unbanned_user_id": userId,
                    "reason": reason,
                    "guild_name": guild.name,
                },
            }

        except ValueError:
            return {"success": False, "error": "Invalid guild ID or user ID format"}
        except discord.Forbidden:
            return {"success": False, "error": "Bot lacks permission to unban members"}
        except discord.NotFound:
            return {"success": False, "error": "User is not banned from this server"}
        except discord.HTTPException as e:
            return {"success": False, "error": f"Discord API error: {e}"}
        except Exception as e:
            logger.error(f"Error unbanning member: {e}")
            return {"success": False, "error": f"Unexpected error: {e}"}

    @app.tool()
    async def discord_timeout_member(
        guildId: str,
        userId: str,
        durationMinutes: int = 0,
        reason: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Times out or removes timeout from a guild member."""
        try:
            guild = client.get_guild(int(guildId))
            if not guild:
                return {
                    "success": False,
                    "error": f"Guild {guildId} not found or bot not in guild",
                }

            # Check bot permissions
            bot_member = guild.get_member(client.user.id) if client.user else None
            if not bot_member or not bot_member.guild_permissions.moderate_members:
                return {
                    "success": False,
                    "error": "Bot lacks moderate_members permission",
                }

            # Get member
            member = await guild.fetch_member(int(userId))
            if not member:
                return {
                    "success": False,
                    "error": f"Member {userId} not found in guild",
                }

            # Check hierarchy (bot's role must be higher than target)
            if bot_member.top_role <= member.top_role:
                return {
                    "success": False,
                    "error": "Bot's role is not high enough to timeout this member",
                }

            # Check if target is guild owner
            if member.id == guild.owner_id:
                return {"success": False, "error": "Cannot timeout the guild owner"}

            import datetime

            if durationMinutes > 0:
                # Apply timeout
                timeout_until = discord.utils.utcnow() + datetime.timedelta(
                    minutes=durationMinutes
                )
                await member.timeout(
                    timeout_until, reason=reason or "Timed out via Discord MCP"
                )

                return {
                    "success": True,
                    "data": {
                        "message": f"Successfully timed out {member.display_name} for {durationMinutes} minutes",
                        "member_id": str(userId),
                        "timeout_until": timeout_until.isoformat(),
                        "duration_minutes": durationMinutes,
                        "reason": reason,
                        "guild_name": guild.name,
                    },
                }
            else:
                # Remove timeout
                await member.timeout(
                    None, reason=reason or "Timeout removed via Discord MCP"
                )

                return {
                    "success": True,
                    "data": {
                        "message": f"Successfully removed timeout from {member.display_name}",
                        "member_id": str(userId),
                        "timeout_removed": True,
                        "reason": reason,
                        "guild_name": guild.name,
                    },
                }

        except ValueError:
            return {"success": False, "error": "Invalid guild ID or user ID format"}
        except discord.NotFound:
            return {"success": False, "error": "Guild or member not found"}
        except discord.Forbidden:
            return {
                "success": False,
                "error": "Bot lacks permission to timeout members",
            }
        except discord.HTTPException as e:
            return {"success": False, "error": f"Discord API error: {e}"}
        except Exception as e:
            logger.error(f"Error timing out member: {e}")
            return {"success": False, "error": f"Unexpected error: {e}"}

    @app.tool()
    async def discord_list_bans(
        guild_id: str,
        limit: Optional[int] = None,
        before: Optional[str] = None,
        after: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List bans in a guild (paginated)."""
        try:
            guild = client.get_guild(int(guild_id))
            if not guild:
                return {
                    "success": False,
                    "error": f"Guild {guild_id} not found or bot not in guild",
                }

            # Check bot permissions
            if not client.user:
                return {"success": False, "error": "Client user not available"}

            bot_member = guild.get_member(client.user.id)
            if not bot_member or not bot_member.guild_permissions.ban_members:
                return {
                    "success": False,
                    "error": "Bot lacks ban_members permission",
                }

            # Validate limit
            if limit is not None and (limit < 1 or limit > 1000):
                return {"success": False, "error": "Limit must be between 1 and 1000"}

            # Get bans using HTTP API since py-cord doesn't have a direct method
            token = await _get_bot_token()
            if not token:
                return {"success": False, "error": "Unable to get bot token"}

            headers = {"Authorization": f"Bot {token}"}
            query_params = []
            if limit:
                query_params.append(f"limit={limit}")
            if before:
                query_params.append(f"before={before}")
            if after:
                query_params.append(f"after={after}")

            query_string = "&".join(query_params) if query_params else ""
            url = f"https://discord.com/api/v10/guilds/{guild_id}/bans"
            if query_string:
                url += f"?{query_string}"

            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        bans_data = await response.json()
                        bans = []

                        for ban in bans_data:
                            ban_info = {
                                "user": {
                                    "id": ban["user"]["id"],
                                    "username": ban["user"]["username"],
                                    "discriminator": ban["user"].get(
                                        "discriminator", "0"
                                    ),
                                    "avatar": ban["user"].get("avatar"),
                                },
                                "reason": ban.get("reason"),
                            }
                            bans.append(ban_info)

                        return {
                            "success": True,
                            "data": {
                                "guild_id": guild_id,
                                "bans": bans,
                                "total_count": len(bans),
                            },
                        }
                    else:
                        error_text = await response.text()
                        return {
                            "success": False,
                            "error": f"Failed to list bans: {response.status} - {error_text}",
                        }

        except ValueError:
            return {"success": False, "error": "Invalid guild ID format"}
        except Exception as e:
            logger.error(f"Error listing bans: {e}")
            return {"success": False, "error": f"Unexpected error: {e}"}

    @app.tool()
    async def discord_ban_user(
        guild_id: str,
        user_id: str,
        delete_message_seconds: Optional[int] = 0,
        reason: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Ban a user from a guild."""
        try:
            guild = client.get_guild(int(guild_id))
            if not guild:
                return {
                    "success": False,
                    "error": f"Guild {guild_id} not found or bot not in guild",
                }

            # Check bot permissions
            if not client.user:
                return {"success": False, "error": "Client user not available"}

            bot_member = guild.get_member(client.user.id)
            if not bot_member or not bot_member.guild_permissions.ban_members:
                return {
                    "success": False,
                    "error": "Bot lacks ban_members permission",
                }

            # Validate delete_message_seconds
            if delete_message_seconds is not None and (
                delete_message_seconds < 0 or delete_message_seconds > 604800
            ):
                return {
                    "success": False,
                    "error": "delete_message_seconds must be between 0 and 604800",
                }

            # Validate reason length
            if reason and len(reason) > 512:
                return {
                    "success": False,
                    "error": "Reason must be 512 characters or less",
                }

            # Ban the user using HTTP API
            token = await _get_bot_token()
            if not token:
                return {"success": False, "error": "Unable to get bot token"}

            headers = {
                "Authorization": f"Bot {token}",
                "Content-Type": "application/json",
            }
            body = {}
            if delete_message_seconds and delete_message_seconds > 0:
                body["delete_message_seconds"] = delete_message_seconds

            url = f"https://discord.com/api/v10/guilds/{guild_id}/bans/{user_id}"

            async with aiohttp.ClientSession() as session:
                async with session.put(url, headers=headers, json=body) as response:
                    if response.status == 204:
                        return {
                            "success": True,
                            "data": {
                                "banned_user_id": user_id,
                                "guild_id": guild_id,
                                "delete_message_seconds": delete_message_seconds or 0,
                                "reason": reason,
                            },
                        }
                    else:
                        error_text = await response.text()
                        return {
                            "success": False,
                            "error": f"Failed to ban user: {response.status} - {error_text}",
                        }

        except ValueError:
            return {"success": False, "error": "Invalid guild ID or user ID format"}
        except Exception as e:
            logger.error(f"Error banning user: {e}")
            return {"success": False, "error": f"Unexpected error: {e}"}

    @app.tool()
    async def discord_unban_user(
        guild_id: str, user_id: str, reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """Remove a ban from a user in a guild."""
        try:
            guild = client.get_guild(int(guild_id))
            if not guild:
                return {
                    "success": False,
                    "error": f"Guild {guild_id} not found or bot not in guild",
                }

            # Check bot permissions
            if not client.user:
                return {"success": False, "error": "Client user not available"}

            bot_member = guild.get_member(client.user.id)
            if not bot_member or not bot_member.guild_permissions.ban_members:
                return {
                    "success": False,
                    "error": "Bot lacks ban_members permission",
                }

            # Validate reason length
            if reason and len(reason) > 512:
                return {
                    "success": False,
                    "error": "Reason must be 512 characters or less",
                }

            # Unban the user using HTTP API
            token = await _get_bot_token()
            if not token:
                return {"success": False, "error": "Unable to get bot token"}

            headers = {"Authorization": f"Bot {token}"}
            url = f"https://discord.com/api/v10/guilds/{guild_id}/bans/{user_id}"

            async with aiohttp.ClientSession() as session:
                async with session.delete(url, headers=headers) as response:
                    if response.status == 204:
                        return {
                            "success": True,
                            "data": {
                                "unbanned_user_id": user_id,
                                "guild_id": guild_id,
                                "reason": reason,
                            },
                        }
                    else:
                        error_text = await response.text()
                        return {
                            "success": False,
                            "error": f"Failed to unban user: {response.status} - {error_text}",
                        }

        except ValueError:
            return {"success": False, "error": "Invalid guild ID or user ID format"}
        except Exception as e:
            logger.error(f"Error unbanning user: {e}")
            return {"success": False, "error": f"Unexpected error: {e}"}

    # Log moderation tool registration
    logger.info(
        "Registered Discord moderation tools: kick_member, ban_member, unban_member, timeout_member, list_bans, ban_user, unban_user"
    )
