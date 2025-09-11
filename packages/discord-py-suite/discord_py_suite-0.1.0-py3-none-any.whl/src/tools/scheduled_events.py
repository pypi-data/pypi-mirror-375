"""Discord scheduled events FastMCP tools."""

from typing import Any, Dict, Optional, List
import discord
from loguru import logger
import aiohttp
from datetime import datetime

try:
    from fastmcp import FastMCP
except ImportError:
    logger.error("FastMCP not installed. Please run: uv add fastmcp>=2.12.0")
    raise


def register_scheduled_events_tools(
    app: FastMCP, client: discord.Client, config: Any
) -> None:
    """Register Discord scheduled events tools with FastMCP app."""

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

    async def _check_permissions(
        guild: discord.Guild, client: discord.Client
    ) -> Dict[str, Any]:
        """Check if bot has required permissions for scheduled events."""
        if not client.user:
            return {"success": False, "error": "Client user not available"}

        bot_member = guild.get_member(client.user.id)
        if not bot_member:
            return {"success": False, "error": "Bot is not a member of this guild"}

        # Check for manage_events permission
        if not bot_member.guild_permissions.manage_events:
            return {"success": False, "error": "Bot lacks manage_events permission"}

        return {"success": True}

    @app.tool()
    async def discord_list_scheduled_events(
        guild_id: str, with_user_count: Optional[bool] = False
    ) -> Dict[str, Any]:
        """List scheduled events in a guild.

        Args:
            guild_id: The guild ID
            with_user_count: Whether to include user count for each event
        """
        try:
            guild = client.get_guild(int(guild_id))
            if not guild:
                return {
                    "success": False,
                    "error": f"Guild {guild_id} not found or bot not in guild",
                }

            # Check basic permissions
            if not client.user:
                return {"success": False, "error": "Client user not available"}

            bot_member = guild.get_member(client.user.id)
            if not bot_member or not bot_member.guild_permissions.view_channel:
                return {"success": False, "error": "Bot lacks view_channel permission"}

            # Get events using HTTP API
            token = await _get_bot_token()
            if not token:
                return {"success": False, "error": "Unable to get bot token"}

            headers = {"Authorization": f"Bot {token}"}
            query_params = []
            if with_user_count:
                query_params.append("with_user_count=true")

            query_string = "&".join(query_params) if query_params else ""
            url = f"https://discord.com/api/v10/guilds/{guild_id}/scheduled-events"
            if query_string:
                url += f"?{query_string}"

            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        events_data = await response.json()
                        events = []

                        for event in events_data:
                            event_info = {
                                "id": event["id"],
                                "guild_id": event["guild_id"],
                                "channel_id": event.get("channel_id"),
                                "creator_id": event.get("creator_id"),
                                "name": event["name"],
                                "description": event.get("description"),
                                "scheduled_start_time": event["scheduled_start_time"],
                                "scheduled_end_time": event.get("scheduled_end_time"),
                                "privacy_level": event["privacy_level"],
                                "status": event["status"],
                                "entity_type": event["entity_type"],
                                "entity_id": event.get("entity_id"),
                                "entity_metadata": event.get("entity_metadata"),
                                "creator": event.get("creator"),
                                "user_count": event.get("user_count"),
                                "image": event.get("image"),
                            }
                            events.append(event_info)

                        return {
                            "success": True,
                            "data": {
                                "guild_id": guild_id,
                                "events": events,
                                "total_count": len(events),
                            },
                        }
                    else:
                        error_text = await response.text()
                        return {
                            "success": False,
                            "error": f"Failed to list scheduled events: {response.status} - {error_text}",
                        }

        except ValueError:
            return {"success": False, "error": "Invalid guild ID format"}
        except Exception as e:
            logger.error(f"Error listing scheduled events: {e}")
            return {"success": False, "error": f"Unexpected error: {e}"}

    @app.tool()
    async def discord_create_scheduled_event(
        guild_id: str,
        name: str,
        scheduled_start_time: str,
        scheduled_end_time: Optional[str] = None,
        privacy_level: Optional[int] = 2,  # GuildOnly
        entity_type: Optional[int] = 2,  # Voice
        channel_id: Optional[str] = None,
        description: Optional[str] = None,
        entity_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Create a scheduled event in a guild.

        Args:
            guild_id: The guild ID
            name: Event name (max 100 characters)
            scheduled_start_time: ISO 8601 timestamp for start time
            scheduled_end_time: ISO 8601 timestamp for end time (optional)
            privacy_level: Privacy level (1=Public, 2=GuildOnly)
            entity_type: Entity type (1=Stage, 2=Voice, 3=External)
            channel_id: Channel ID for voice/stage events
            description: Event description
            entity_metadata: Metadata for external events
        """
        try:
            guild = client.get_guild(int(guild_id))
            if not guild:
                return {
                    "success": False,
                    "error": f"Guild {guild_id} not found or bot not in guild",
                }

            # Check permissions
            perm_check = await _check_permissions(guild, client)
            if not perm_check["success"]:
                return perm_check

            # Validate inputs
            if len(name) > 100:
                return {
                    "success": False,
                    "error": "Event name must be 100 characters or less",
                }

            if privacy_level not in [1, 2]:
                return {
                    "success": False,
                    "error": "Privacy level must be 1 (Public) or 2 (GuildOnly)",
                }

            if entity_type not in [1, 2, 3]:
                return {
                    "success": False,
                    "error": "Entity type must be 1 (Stage), 2 (Voice), or 3 (External)",
                }

            if entity_type in [1, 2] and not channel_id:
                return {
                    "success": False,
                    "error": "Channel ID required for Stage/Voice events",
                }

            if entity_type == 3 and not entity_metadata:
                return {
                    "success": False,
                    "error": "Entity metadata required for External events",
                }

            # Validate timestamps
            try:
                start_time = datetime.fromisoformat(
                    scheduled_start_time.replace("Z", "+00:00")
                )
                if start_time <= datetime.now(start_time.tzinfo):
                    return {
                        "success": False,
                        "error": "Start time must be in the future",
                    }
            except ValueError:
                return {"success": False, "error": "Invalid start time format"}

            if scheduled_end_time:
                try:
                    end_time = datetime.fromisoformat(
                        scheduled_end_time.replace("Z", "+00:00")
                    )
                    if end_time <= start_time:
                        return {
                            "success": False,
                            "error": "End time must be after start time",
                        }
                except ValueError:
                    return {"success": False, "error": "Invalid end time format"}

            # Get bot token
            token = await _get_bot_token()
            if not token:
                return {"success": False, "error": "Unable to get bot token"}

            # Prepare event data
            event_data: Dict[str, Any] = {
                "name": name,
                "privacy_level": privacy_level,
                "scheduled_start_time": scheduled_start_time,
                "entity_type": entity_type,
            }

            if scheduled_end_time:
                event_data["scheduled_end_time"] = scheduled_end_time
            if channel_id:
                event_data["channel_id"] = channel_id
            if description:
                event_data["description"] = description
            if entity_metadata:
                event_data["entity_metadata"] = entity_metadata

            # Make API request
            headers = {
                "Authorization": f"Bot {token}",
                "Content-Type": "application/json",
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"https://discord.com/api/v10/guilds/{guild_id}/scheduled-events",
                    json=event_data,
                    headers=headers,
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "success": True,
                            "data": {
                                "event_id": result["id"],
                                "guild_id": result["guild_id"],
                                "name": result["name"],
                                "scheduled_start_time": result["scheduled_start_time"],
                                "scheduled_end_time": result.get("scheduled_end_time"),
                                "privacy_level": result["privacy_level"],
                                "status": result["status"],
                                "entity_type": result["entity_type"],
                                "channel_id": result.get("channel_id"),
                                "entity_id": result.get("entity_id"),
                                "entity_metadata": result.get("entity_metadata"),
                                "description": result.get("description"),
                            },
                        }
                    else:
                        error_text = await response.text()
                        return {
                            "success": False,
                            "error": f"Failed to create scheduled event: {response.status} - {error_text}",
                        }

        except ValueError:
            return {"success": False, "error": "Invalid guild ID format"}
        except Exception as e:
            logger.error(f"Error creating scheduled event: {e}")
            return {"success": False, "error": f"Unexpected error: {e}"}

    @app.tool()
    async def discord_delete_scheduled_event(
        guild_id: str, event_id: str
    ) -> Dict[str, Any]:
        """Delete a scheduled event from a guild.

        Args:
            guild_id: The guild ID
            event_id: The scheduled event ID to delete
        """
        try:
            guild = client.get_guild(int(guild_id))
            if not guild:
                return {
                    "success": False,
                    "error": f"Guild {guild_id} not found or bot not in guild",
                }

            # Check permissions
            perm_check = await _check_permissions(guild, client)
            if not perm_check["success"]:
                return perm_check

            # Get bot token
            token = await _get_bot_token()
            if not token:
                return {"success": False, "error": "Unable to get bot token"}

            # Make API request
            headers = {"Authorization": f"Bot {token}"}

            async with aiohttp.ClientSession() as session:
                async with session.delete(
                    f"https://discord.com/api/v10/guilds/{guild_id}/scheduled-events/{event_id}",
                    headers=headers,
                ) as response:
                    if response.status == 204:
                        return {
                            "success": True,
                            "data": {
                                "deleted_event_id": event_id,
                                "guild_id": guild_id,
                            },
                        }
                    else:
                        error_text = await response.text()
                        return {
                            "success": False,
                            "error": f"Failed to delete scheduled event: {response.status} - {error_text}",
                        }

        except ValueError:
            return {"success": False, "error": "Invalid guild ID or event ID format"}
        except Exception as e:
            logger.error(f"Error deleting scheduled event: {e}")
            return {"success": False, "error": f"Unexpected error: {e}"}

    @app.tool()
    async def discord_list_scheduled_event_users(
        guild_id: str,
        event_id: str,
        limit: Optional[int] = None,
        with_member: Optional[bool] = False,
        before: Optional[str] = None,
        after: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List users subscribed to a scheduled event.

        Args:
            guild_id: The guild ID
            event_id: The scheduled event ID
            limit: Maximum number of users to return (1-100)
            with_member: Whether to include member data
            before: User ID to get users before
            after: User ID to get users after
        """
        try:
            guild = client.get_guild(int(guild_id))
            if not guild:
                return {
                    "success": False,
                    "error": f"Guild {guild_id} not found or bot not in guild",
                }

            # Check basic permissions
            if not client.user:
                return {"success": False, "error": "Client user not available"}

            bot_member = guild.get_member(client.user.id)
            if not bot_member or not bot_member.guild_permissions.view_channel:
                return {"success": False, "error": "Bot lacks view_channel permission"}

            # Validate limit
            if limit is not None and (limit < 1 or limit > 100):
                return {"success": False, "error": "Limit must be between 1 and 100"}

            # Get bot token
            token = await _get_bot_token()
            if not token:
                return {"success": False, "error": "Unable to get bot token"}

            # Make API request
            headers = {"Authorization": f"Bot {token}"}
            query_params = []
            if limit:
                query_params.append(f"limit={limit}")
            if with_member:
                query_params.append("with_member=true")
            if before:
                query_params.append(f"before={before}")
            if after:
                query_params.append(f"after={after}")

            query_string = "&".join(query_params) if query_params else ""
            url = f"https://discord.com/api/v10/guilds/{guild_id}/scheduled-events/{event_id}/users"
            if query_string:
                url += f"?{query_string}"

            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        users_data = await response.json()
                        users = []

                        for user_data in users_data:
                            user_info = {
                                "user_id": user_data["user"]["id"],
                                "username": user_data["user"]["username"],
                                "discriminator": user_data["user"].get(
                                    "discriminator", "0"
                                ),
                                "avatar": user_data["user"].get("avatar"),
                                "member": user_data.get("member"),
                            }
                            users.append(user_info)

                        return {
                            "success": True,
                            "data": {
                                "guild_id": guild_id,
                                "event_id": event_id,
                                "users": users,
                                "total_count": len(users),
                            },
                        }
                    else:
                        error_text = await response.text()
                        return {
                            "success": False,
                            "error": f"Failed to list event users: {response.status} - {error_text}",
                        }

        except ValueError:
            return {"success": False, "error": "Invalid guild ID or event ID format"}
        except Exception as e:
            logger.error(f"Error listing scheduled event users: {e}")
            return {"success": False, "error": f"Unexpected error: {e}"}

    # Log scheduled events tool registration
    logger.info(
        "Registered Discord scheduled events tools: list_scheduled_events, create_scheduled_event, delete_scheduled_event, list_scheduled_event_users"
    )
