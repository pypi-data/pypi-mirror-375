"""Basic Discord FastMCP tools."""

from typing import Any, Dict, Optional
import discord
from loguru import logger

try:
    from fastmcp import FastMCP
except ImportError:
    logger.error("FastMCP not installed. Please run: uv add fastmcp>=2.12.0")
    raise


def register_basic_tools(app: FastMCP, client: discord.Client, config: Any) -> None:
    """Register basic Discord tools with FastMCP app."""

    @app.tool()
    async def discord_status() -> Dict[str, Any]:
        """Get Discord login status and client information."""
        is_ready = client.is_ready()

        status: Dict[str, Any] = {
            "logged_in": is_ready,
            "configured": config.discord_token is not None,
            "client_status": "ready" if is_ready else "not_ready",
        }

        if is_ready and client.user:
            status.update(
                {
                    "user": {
                        "id": str(client.user.id),
                        "name": client.user.name,
                        "discriminator": client.user.discriminator,
                    },
                    "guilds": len(client.guilds),
                    "channels": len([c for g in client.guilds for c in g.channels]),
                }
            )

        return {"success": True, "data": status}

    @app.tool()
    async def discord_get_server_info(guild_id: str) -> Dict[str, Any]:
        """Get information about a Discord server.

        Args:
            guild_id: The Discord server (guild) ID

        Returns:
            Server information including name, member count, channels, etc.
        """
        try:
            guild = client.get_guild(int(guild_id))
            if not guild:
                return {
                    "success": False,
                    "error": f"Guild {guild_id} not found or bot not in guild",
                }

            return {
                "success": True,
                "data": {
                    "id": str(guild.id),
                    "name": guild.name,
                    "description": guild.description,
                    "member_count": guild.member_count,
                    "channel_count": len(guild.channels),
                    "role_count": len(guild.roles),
                    "emoji_count": len(guild.emojis),
                    "boost_level": guild.premium_tier,
                    "boost_count": guild.premium_subscription_count,
                    "verification_level": str(guild.verification_level),
                    "created_at": guild.created_at.isoformat(),
                },
            }
        except ValueError:
            return {"success": False, "error": "Invalid guild ID format"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @app.tool()
    async def discord_login(token: Optional[str] = None) -> Dict[str, Any]:
        """Login to Discord using the configured or provided token."""
        try:
            # Use provided token or fall back to config
            auth_token = token or config.discord_token

            if not auth_token:
                return {
                    "success": False,
                    "error": "No Discord token provided or configured",
                }

            # If client is already connected, disconnect first
            if not client.is_closed():
                await client.close()

            # Start the client with token
            await client.login(auth_token)

            return {
                "success": True,
                "data": {
                    "status": "logged_in",
                    "user_id": str(client.user.id) if client.user else None,
                    "username": client.user.name if client.user else None,
                },
            }

        except discord.LoginFailure:
            return {"success": False, "error": "Invalid Discord token"}
        except Exception as e:
            return {"success": False, "error": f"Login failed: {str(e)}"}

    @app.tool()
    async def discord_logout() -> Dict[str, Any]:
        """Logout from Discord and disconnect the client."""
        try:
            if client.is_closed():
                return {"success": False, "error": "Client is not logged in"}

            username = client.user.name if client.user else "Unknown"
            await client.close()

            return {
                "success": True,
                "data": {
                    "status": "logged_out",
                    "previous_user": username,
                },
            }

        except Exception as e:
            return {"success": False, "error": f"Logout failed: {str(e)}"}

    @app.tool()
    async def discord_login_status() -> Dict[str, Any]:
        """Show current login status, configuration, and health information."""
        try:
            is_ready = client.is_ready()
            is_closed = client.is_closed()

            status_data = {
                "logged_in": not is_closed and is_ready,
                "client_ready": is_ready,
                "client_closed": is_closed,
                "token_configured": config.discord_token is not None,
                "latency_ms": round(client.latency * 1000) if is_ready else None,
            }

            if is_ready and client.user:
                status_data.update(
                    {
                        "bot_info": {
                            "id": str(client.user.id),
                            "username": client.user.name,
                            "discriminator": client.user.discriminator,
                            "verified": client.user.verified,
                            "bot": client.user.bot,
                        },
                        "guild_count": len(client.guilds),
                        "permissions": {
                            "can_send_messages": True,  # Basic assumption
                            "can_read_messages": True,  # Basic assumption
                        },
                    }
                )

            return {"success": True, "data": status_data}

        except Exception as e:
            return {"success": False, "error": f"Status check failed: {str(e)}"}

    @app.tool()
    async def discord_set_token(token: str) -> Dict[str, Any]:
        """Set and save a Discord bot token for authentication."""
        try:
            if not token or not isinstance(token, str):
                return {"success": False, "error": "Invalid token format"}

            # Basic token format validation
            if not token.startswith(("Bot ", "MTA", "MTI", "ODA", "ODI", "ODE")):
                return {"success": False, "error": "Token format appears invalid"}

            # Update config
            config.discord_token = token

            return {
                "success": True,
                "data": {
                    "status": "token_saved",
                    "token_prefix": token[:10] + "..." if len(token) > 10 else "***",
                },
            }

        except Exception as e:
            return {"success": False, "error": f"Token save failed: {str(e)}"}

    @app.tool()
    async def discord_validate_token() -> Dict[str, Any]:
        """Validate the format and basic structure of the configured Discord token."""
        try:
            token = config.discord_token

            if not token:
                return {"success": False, "error": "No token configured"}

            validation_results = {
                "token_exists": True,
                "format_valid": False,
                "length_valid": False,
                "prefix_valid": False,
            }

            # Check basic format
            if isinstance(token, str) and len(token) > 20:
                validation_results["length_valid"] = True

            # Check prefix (common Discord bot token patterns)
            if token.startswith(("Bot ", "MTA", "MTI", "ODA", "ODI", "ODE")):
                validation_results["prefix_valid"] = True

            # Overall format validation
            validation_results["format_valid"] = (
                validation_results["length_valid"]
                and validation_results["prefix_valid"]
            )

            return {
                "success": True,
                "data": {
                    "validation": validation_results,
                    "token_preview": token[:15] + "..." if len(token) > 15 else "***",
                    "can_attempt_login": validation_results["format_valid"],
                },
            }

        except Exception as e:
            return {"success": False, "error": f"Token validation failed: {str(e)}"}

    @app.tool()
    async def discord_update_config(**kwargs) -> Dict[str, Any]:
        """Update server configuration settings at runtime."""
        try:
            updated_settings = {}

            # Map of allowed configuration updates
            config_mappings = {
                "ALLOW_GUILD_IDS": "allowed_guild_ids",
                "ALLOW_CHANNEL_IDS": "allowed_channel_ids",
                "ENABLE_USER_MANAGEMENT": "enable_user_management",
                "ENABLE_VOICE_CHANNELS": "enable_voice_channels",
                "ENABLE_DIRECT_MESSAGES": "enable_direct_messages",
                "ENABLE_SERVER_MANAGEMENT": "enable_server_management",
                "ENABLE_RBAC": "enable_rbac",
                "ENABLE_CONTENT_MANAGEMENT": "enable_content_management",
                "TRANSPORT": "transport",
                "HTTP_PORT": "port",
            }

            for key, value in kwargs.items():
                if key in config_mappings:
                    config_attr = config_mappings[key]
                    if hasattr(config, config_attr):
                        setattr(config, config_attr, value)
                        updated_settings[key] = value

            return {
                "success": True,
                "data": {
                    "updated_settings": updated_settings,
                    "message": f"Updated {len(updated_settings)} configuration settings",
                },
            }

        except Exception as e:
            return {"success": False, "error": f"Config update failed: {str(e)}"}

    @app.tool()
    async def discord_health_check() -> Dict[str, Any]:
        """Perform a comprehensive health check of the Discord MCP server."""
        try:
            health_data = {
                "overall_status": "healthy",
                "timestamp": discord.utils.utcnow().isoformat(),
                "checks": {},
            }

            # Check Discord connection
            if client.is_ready():
                health_data["checks"]["discord_connection"] = {
                    "status": "healthy",
                    "latency_ms": round(client.latency * 1000),
                    "guilds_connected": len(client.guilds),
                }
            else:
                health_data["checks"]["discord_connection"] = {
                    "status": "unhealthy",
                    "error": "Client not ready",
                }
                health_data["overall_status"] = "degraded"

            # Check configuration
            health_data["checks"]["configuration"] = {
                "status": "healthy" if config.discord_token else "unhealthy",
                "token_configured": config.discord_token is not None,
                "transport_type": config.transport,
            }

            if not config.discord_token:
                health_data["overall_status"] = "unhealthy"

            # Check permissions in a sample guild (if available)
            if client.guilds:
                sample_guild = client.guilds[0]
                bot_member = (
                    sample_guild.get_member(client.user.id) if client.user else None
                )

                if bot_member:
                    perms = bot_member.guild_permissions
                    health_data["checks"]["permissions"] = {
                        "status": "healthy",
                        "sample_guild": sample_guild.name,
                        "key_permissions": {
                            "send_messages": perms.send_messages,
                            "read_messages": perms.read_messages,
                            "manage_channels": perms.manage_channels,
                            "manage_roles": perms.manage_roles,
                        },
                    }

            # Memory and performance check (basic)
            health_data["checks"]["performance"] = {
                "status": "healthy",
                "cached_guilds": len(client.guilds),
                "cached_users": len(client.users),
            }

            return {"success": True, "data": health_data}

        except Exception as e:
            return {"success": False, "error": f"Health check failed: {str(e)}"}

    @app.tool()
    async def discord_list_servers() -> Dict[str, Any]:
        """List all Discord servers that the bot has access to."""
        try:
            if not client.is_ready():
                return {"success": False, "error": "Client not ready"}

            servers = []
            for guild in client.guilds:
                server_info = {
                    "id": str(guild.id),
                    "name": guild.name,
                    "member_count": guild.member_count,
                    "channel_count": len(guild.channels),
                    "role_count": len(guild.roles),
                    "boost_level": guild.premium_tier,
                    "verification_level": str(guild.verification_level),
                    "large": guild.large,
                    "icon_url": str(guild.icon) if guild.icon else None,
                }
                servers.append(server_info)

            return {
                "success": True,
                "data": {
                    "servers": servers,
                    "total_count": len(servers),
                },
            }

        except Exception as e:
            return {"success": False, "error": f"Failed to list servers: {str(e)}"}

    # Log basic tool registration
    logger.info(
        "Registered Discord basic tools: status, server_info, login, logout, login_status, set_token, validate_token, update_config, health_check, list_servers"
    )
