"""Discord server management FastMCP tools."""

from typing import Any, Dict, Optional, List
import discord
from loguru import logger

try:
    from fastmcp import FastMCP
except ImportError:
    logger.error("FastMCP not installed. Please run: uv add fastmcp>=2.12.0")
    raise


def register_server_tools(app: FastMCP, client: discord.Client, config: Any) -> None:
    """Register Discord server management tools with FastMCP app."""

    @app.tool()
    async def discord_update_server_settings(
        guildId: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        icon: Optional[str] = None,
        banner: Optional[str] = None,
        splash: Optional[str] = None,
        discoverySplash: Optional[str] = None,
        afkChannelId: Optional[str] = None,
        afkTimeout: Optional[int] = None,
        defaultMessageNotifications: Optional[str] = None,
        explicitContentFilter: Optional[str] = None,
        verificationLevel: Optional[str] = None,
        reason: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Updates various server settings like name, description, icon, etc."""
        try:
            guild = client.get_guild(int(guildId))
            if not guild:
                return {
                    "success": False,
                    "error": f"Guild {guildId} not found or bot not in guild",
                }

            # Check bot permissions
            bot_member = guild.get_member(client.user.id) if client.user else None
            if not bot_member or not bot_member.guild_permissions.manage_guild:
                return {
                    "success": False,
                    "error": "Bot lacks manage_guild permission",
                }

            # Prepare edit arguments
            edit_kwargs = {}
            if name is not None:
                edit_kwargs["name"] = name
            if description is not None:
                edit_kwargs["description"] = description
            if icon is not None:
                edit_kwargs["icon"] = icon
            if banner is not None:
                edit_kwargs["banner"] = banner
            if splash is not None:
                edit_kwargs["splash"] = splash
            if discoverySplash is not None:
                edit_kwargs["discovery_splash"] = discoverySplash
            if afkChannelId is not None:
                afk_channel = guild.get_channel(int(afkChannelId))
                if afk_channel and isinstance(afk_channel, discord.VoiceChannel):
                    edit_kwargs["afk_channel"] = afk_channel
            if afkTimeout is not None:
                edit_kwargs["afk_timeout"] = afkTimeout
            if defaultMessageNotifications is not None:
                if defaultMessageNotifications == "ALL_MESSAGES":
                    edit_kwargs["default_notifications"] = (
                        discord.NotificationLevel.all_messages
                    )
                elif defaultMessageNotifications == "ONLY_MENTIONS":
                    edit_kwargs["default_notifications"] = (
                        discord.NotificationLevel.only_mentions
                    )
            if explicitContentFilter is not None:
                if explicitContentFilter == "DISABLED":
                    edit_kwargs["explicit_content_filter"] = (
                        discord.ContentFilter.disabled
                    )
                elif explicitContentFilter == "MEMBERS_WITHOUT_ROLES":
                    edit_kwargs["explicit_content_filter"] = (
                        discord.ContentFilter.no_role
                    )
                elif explicitContentFilter == "ALL_MEMBERS":
                    edit_kwargs["explicit_content_filter"] = (
                        discord.ContentFilter.all_members
                    )
            if verificationLevel is not None:
                verification_map = {
                    "NONE": discord.VerificationLevel.none,
                    "LOW": discord.VerificationLevel.low,
                    "MEDIUM": discord.VerificationLevel.medium,
                    "HIGH": discord.VerificationLevel.high,
                    "VERY_HIGH": discord.VerificationLevel.highest,
                }
                if verificationLevel in verification_map:
                    edit_kwargs["verification_level"] = verification_map[
                        verificationLevel
                    ]
            if reason:
                edit_kwargs["reason"] = reason

            await guild.edit(**edit_kwargs)

            return {
                "success": True,
                "data": {
                    "guild_id": str(guildId),
                    "updated_settings": list(edit_kwargs.keys()),
                    "guild_name": guild.name,
                },
            }

        except ValueError:
            return {"success": False, "error": "Invalid guild ID or channel ID format"}
        except discord.Forbidden:
            return {"success": False, "error": "Bot lacks permission to manage guild"}
        except discord.HTTPException as e:
            return {"success": False, "error": f"Discord API error: {e}"}
        except Exception as e:
            logger.error(f"Error updating server settings: {e}")
            return {"success": False, "error": f"Unexpected error: {e}"}

    @app.tool()
    async def discord_update_server_engagement(
        guildId: str,
        systemChannelId: Optional[str] = None,
        systemChannelFlags: Optional[List[str]] = None,
        rulesChannelId: Optional[str] = None,
        publicUpdatesChannelId: Optional[str] = None,
        preferredLocale: Optional[str] = None,
        reason: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Updates server engagement settings like system messages and rules."""
        try:
            guild = client.get_guild(int(guildId))
            if not guild:
                return {
                    "success": False,
                    "error": f"Guild {guildId} not found or bot not in guild",
                }

            # Check bot permissions
            bot_member = guild.get_member(client.user.id) if client.user else None
            if not bot_member or not bot_member.guild_permissions.manage_guild:
                return {
                    "success": False,
                    "error": "Bot lacks manage_guild permission",
                }

            # Prepare edit arguments
            edit_kwargs = {}
            if systemChannelId is not None:
                system_channel = guild.get_channel(int(systemChannelId))
                if system_channel and isinstance(system_channel, discord.TextChannel):
                    edit_kwargs["system_channel"] = system_channel
            if systemChannelFlags is not None:
                flags = discord.SystemChannelFlags()
                for flag in systemChannelFlags:
                    if hasattr(flags, flag.lower()):
                        setattr(flags, flag.lower(), True)
                edit_kwargs["system_channel_flags"] = flags
            if rulesChannelId is not None:
                rules_channel = guild.get_channel(int(rulesChannelId))
                if rules_channel and isinstance(rules_channel, discord.TextChannel):
                    edit_kwargs["rules_channel"] = rules_channel
            if publicUpdatesChannelId is not None:
                updates_channel = guild.get_channel(int(publicUpdatesChannelId))
                if updates_channel and isinstance(updates_channel, discord.TextChannel):
                    edit_kwargs["public_updates_channel"] = updates_channel
            if preferredLocale is not None:
                edit_kwargs["preferred_locale"] = preferredLocale
            if reason:
                edit_kwargs["reason"] = reason

            await guild.edit(**edit_kwargs)

            return {
                "success": True,
                "data": {
                    "guild_id": str(guildId),
                    "updated_settings": list(edit_kwargs.keys()),
                    "guild_name": guild.name,
                },
            }

        except ValueError:
            return {"success": False, "error": "Invalid guild ID or channel ID format"}
        except discord.Forbidden:
            return {"success": False, "error": "Bot lacks permission to manage guild"}
        except discord.HTTPException as e:
            return {"success": False, "error": f"Discord API error: {e}"}
        except Exception as e:
            logger.error(f"Error updating server engagement: {e}")
            return {"success": False, "error": f"Unexpected error: {e}"}

    @app.tool()
    async def discord_update_welcome_screen(
        guildId: str,
        enabled: Optional[bool] = None,
        welcomeChannels: Optional[List[Dict[str, Any]]] = None,
        description: Optional[str] = None,
        reason: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Updates the server's welcome screen settings."""
        try:
            guild = client.get_guild(int(guildId))
            if not guild:
                return {
                    "success": False,
                    "error": f"Guild {guildId} not found or bot not in guild",
                }

            # Check bot permissions
            bot_member = guild.get_member(client.user.id) if client.user else None
            if not bot_member or not bot_member.guild_permissions.manage_guild:
                return {
                    "success": False,
                    "error": "Bot lacks manage_guild permission",
                }

            # Welcome screen updates require complex WelcomeScreen API implementation
            # For now, return not implemented
            return {
                "success": False,
                "error": "Welcome screen updates require complex WelcomeScreen API implementation - not yet supported",
                "note": "This feature requires detailed WelcomeScreen and WelcomeChannel object handling",
            }

        except ValueError:
            return {"success": False, "error": "Invalid guild ID format"}
        except discord.Forbidden:
            return {"success": False, "error": "Bot lacks permission to manage guild"}
        except discord.HTTPException as e:
            return {"success": False, "error": f"Discord API error: {e}"}
        except Exception as e:
            logger.error(f"Error updating welcome screen: {e}")
            return {"success": False, "error": f"Unexpected error: {e}"}

    # Log server tool registration
    logger.info(
        "Registered Discord server management tools: update_server_settings, update_server_engagement, update_welcome_screen"
    )
