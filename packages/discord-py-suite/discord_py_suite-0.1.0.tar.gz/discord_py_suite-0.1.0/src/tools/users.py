"""Discord user management FastMCP tools."""

from typing import Any, Dict, Optional, List
import discord
from loguru import logger

try:
    from fastmcp import FastMCP
except ImportError:
    logger.error("FastMCP not installed. Please run: uv add fastmcp>=2.12.0")
    raise


def register_user_tools(app: FastMCP, client: discord.Client, config: Any) -> None:
    """Register Discord user management tools with FastMCP app."""

    @app.tool()
    async def discord_get_user_info(user_id: str) -> Dict[str, Any]:
        """Get information about a Discord user."""
        try:
            user = await client.fetch_user(int(user_id))
            if not user:
                return {"success": False, "error": f"User {user_id} not found"}

            user_data = {
                "id": str(user.id),
                "username": user.name,
                "display_name": user.display_name,
                "discriminator": user.discriminator
                if user.discriminator != "0"
                else None,
                "avatar_url": str(user.avatar.url) if user.avatar else None,
                "default_avatar_url": str(user.default_avatar.url),
                "bot": user.bot,
                "system": user.system,
                "created_at": user.created_at.isoformat(),
                "public_flags": user.public_flags.value,
                "banner_url": str(user.banner.url) if user.banner else None,
                "accent_color": user.accent_color.value if user.accent_color else None,
            }

            return {"success": True, "data": user_data}

        except ValueError:
            return {"success": False, "error": "Invalid user ID format"}
        except discord.NotFound:
            return {"success": False, "error": "User not found"}
        except discord.HTTPException as e:
            return {"success": False, "error": f"Discord API error: {e}"}
        except Exception as e:
            logger.error(f"Error getting user info: {e}")
            return {"success": False, "error": f"Unexpected error: {e}"}

    @app.tool()
    async def discord_get_member_info(guild_id: str, user_id: str) -> Dict[str, Any]:
        """Get information about a Discord guild member."""
        try:
            guild = client.get_guild(int(guild_id))
            if not guild:
                return {
                    "success": False,
                    "error": f"Guild {guild_id} not found or bot not in guild",
                }

            member = await guild.fetch_member(int(user_id))
            if not member:
                return {
                    "success": False,
                    "error": f"Member {user_id} not found in guild",
                }

            return {
                "success": True,
                "data": {
                    "user": {
                        "id": str(member.id),
                        "username": member.name,
                        "display_name": member.display_name,
                        "discriminator": member.discriminator
                        if member.discriminator != "0"
                        else None,
                        "avatar_url": str(member.avatar.url) if member.avatar else None,
                        "bot": member.bot,
                    },
                    "guild_info": {
                        "nickname": member.nick,
                        "joined_at": member.joined_at.isoformat()
                        if member.joined_at
                        else None,
                        "premium_since": member.premium_since.isoformat()
                        if member.premium_since
                        else None,
                        "pending": member.pending,
                        "timed_out_until": getattr(member, "timed_out_until", None),
                        "communication_disabled_until": getattr(
                            member, "communication_disabled_until", None
                        ),
                    },
                    "roles": [
                        {
                            "id": str(role.id),
                            "name": role.name,
                            "color": role.color.value,
                            "position": role.position,
                            "managed": role.managed,
                            "mentionable": role.mentionable,
                        }
                        for role in member.roles[1:]  # Skip @everyone
                    ],
                    "permissions": [
                        perm for perm, value in member.guild_permissions if value
                    ],
                    "top_role": {
                        "id": str(member.top_role.id),
                        "name": member.top_role.name,
                        "color": member.top_role.color.value,
                    }
                    if member.top_role
                    else None,
                },
            }

        except ValueError:
            return {"success": False, "error": "Invalid guild ID or user ID format"}
        except discord.NotFound:
            return {"success": False, "error": "Guild or member not found"}
        except discord.Forbidden:
            return {
                "success": False,
                "error": "Bot lacks permission to access member information",
            }
        except discord.HTTPException as e:
            return {"success": False, "error": f"Discord API error: {e}"}
        except Exception as e:
            logger.error(f"Error getting member info: {e}")
            return {"success": False, "error": f"Unexpected error: {e}"}
