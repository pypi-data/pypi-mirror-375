"""Modular FastMCP Server implementation for Discord-Py-Suite."""

import asyncio
from typing import Any, Dict, List, Optional, Union
import json

import discord
from loguru import logger

try:
    from fastmcp import FastMCP
except ImportError:
    logger.error("FastMCP not installed. Please run: uv add fastmcp>=2.12.0")
    raise

from .config import Config
from .routes import route_handler, setup_default_routes
from .tools import (
    register_basic_tools,
    register_messaging_tools,
    register_user_tools,
    register_channel_tools,
    register_moderation_tools,
    register_voice_tools,
    register_webhook_tools,
    register_roles_tools,
    register_forum_tools,
    register_server_tools,
    register_content_tools,
    register_soundboard_tools,
    register_scheduled_events_tools,
    register_stickers_tools,
    register_thread_tools,
    register_auto_moderation_tools,
    register_audit_logs_tools,
    register_stage_instances_tools,
    register_raw_rest_tools,
    register_advanced_operations_tools,
    register_guild_templates_tools,
    register_welcome_screen_tools,
    register_slash_commands_tools,
)


class DiscordMCPServer:
    """Main FastMCP server for Discord integration with modular tool architecture."""

    def __init__(self, discord_client: discord.Client, config: Config):
        self.discord_client = discord_client
        self.config = config
        self.app = FastMCP("Discord-Py-Suite")
        self._setup_tools()
        self._setup_routes()

    def _setup_tools(self) -> None:
        """Set up all FastMCP tools using modular tool registrations."""

        # Register all tool modules
        register_basic_tools(self.app, self.discord_client, self.config)
        register_messaging_tools(self.app, self.discord_client, self.config)
        register_user_tools(self.app, self.discord_client, self.config)
        register_channel_tools(self.app, self.discord_client, self.config)
        register_moderation_tools(self.app, self.discord_client, self.config)
        register_voice_tools(self.app, self.discord_client, self.config)
        register_webhook_tools(self.app, self.discord_client, self.config)
        register_roles_tools(self.app, self.discord_client, self.config)
        register_forum_tools(self.app, self.discord_client, self.config)
        register_server_tools(self.app, self.discord_client, self.config)
        register_content_tools(self.app, self.discord_client, self.config)
        register_soundboard_tools(self.app, self.discord_client, self.config)
        register_scheduled_events_tools(self.app, self.discord_client, self.config)
        register_stickers_tools(self.app, self.discord_client, self.config)
        register_thread_tools(self.app, self.discord_client, self.config)
        register_auto_moderation_tools(self.app, self.discord_client, self.config)
        register_audit_logs_tools(self.app, self.discord_client, self.config)
        register_stage_instances_tools(self.app, self.discord_client, self.config)
        register_raw_rest_tools(self.app, self.discord_client, self.config)
        register_advanced_operations_tools(self.app, self.discord_client, self.config)
        register_guild_templates_tools(self.app, self.discord_client, self.config)
        register_welcome_screen_tools(self.app, self.discord_client, self.config)
        register_slash_commands_tools(self.app, self.discord_client, self.config)

        logger.info("Modular FastMCP Discord tools registered successfully")
        logger.info(
            f"Tool modules loaded: Basic, Messaging, Users, Channels, Moderation, Voice, Webhooks, Roles, Forum, Server, Content, Soundboard, ScheduledEvents, Stickers, Threads, AutoModeration, AuditLogs, StageInstances, RawRest, AdvancedOperations, GuildTemplates, WelcomeScreen, SlashCommands"
        )

    def _setup_routes(self) -> None:
        """Set up HTTP routes for webhooks and integrations using FastMCP."""
        if not self.config.enable_route_handling:
            logger.info("Route handling disabled in configuration")
            return

        # Set up default Discord routes
        setup_default_routes()

        # Add route-based tools to FastMCP
        self._register_route_tools()

        logger.info("HTTP route handling configured with FastMCP")

    def _register_route_tools(self) -> None:
        """Register route-based tools with FastMCP."""

        @self.app.tool()
        async def discord_webhook_info(
            webhook_id: str, webhook_token: str
        ) -> Dict[str, Any]:
            """Get information about a Discord webhook."""
            try:
                # This would typically make an API call to Discord
                # For now, return mock data
                return {
                    "success": True,
                    "data": {
                        "id": webhook_id,
                        "token": webhook_token[:10] + "...",  # Mask token
                        "type": 1,  # Incoming webhook
                        "guild_id": None,
                        "channel_id": None,
                        "name": "Test Webhook",
                        "avatar": None,
                        "application_id": None,
                    },
                }
            except Exception as e:
                logger.error(f"Error getting webhook info: {e}")
                return {"success": False, "error": str(e)}

        @self.app.tool()
        async def discord_route_status() -> Dict[str, Any]:
            """Get status of all registered routes."""
            try:
                routes = route_handler.get_routes_info()
                return {
                    "success": True,
                    "data": {
                        "total_routes": len(routes),
                        "routes": routes,
                        "route_handling_enabled": self.config.enable_route_handling,
                    },
                }
            except Exception as e:
                logger.error(f"Error getting route status: {e}")
                return {"success": False, "error": str(e)}

        logger.info("Route-based tools registered with FastMCP")

    async def start(self) -> None:
        """Start the FastMCP server with route handling support."""
        logger.info("Starting Discord-Py-Suite FastMCP server (Modular)")

        # Start Discord client if not already connected
        if not self.discord_client.is_ready() and self.config.discord_token:
            try:
                # Start the client in the background
                asyncio.create_task(
                    self.discord_client.start(self.config.discord_token)
                )

                # Wait for client to be ready
                while not self.discord_client.is_ready():
                    await asyncio.sleep(0.1)

            except Exception as e:
                logger.warning(f"Failed to start Discord client: {e}")

        # Start the server based on transport type
        if self.config.transport == "stdio":
            logger.info("Starting FastMCP with stdio transport")
            self.app.run("stdio")
        elif self.config.transport in ["http", "websocket"]:
            await self._start_http_server()
        else:
            logger.error(f"Transport type '{self.config.transport}' not supported")
            raise NotImplementedError(
                f"Transport '{self.config.transport}' not supported"
            )

    async def _start_http_server(self) -> None:
        """Start HTTP server with FastMCP's native HTTP support."""
        logger.info(
            f"Starting FastMCP HTTP server on {self.config.host}:{self.config.port}"
        )

        # Use FastMCP's built-in HTTP server
        # This will handle both MCP protocol and any additional HTTP routes
        try:
            self.app.run("http", host=self.config.host, port=self.config.port)
        except Exception as e:
            logger.error(f"Failed to start HTTP server: {e}")
            raise

    async def stop(self) -> None:
        """Stop the FastMCP server."""
        logger.info("Stopping Discord-Py-Suite FastMCP server")

        # Close Discord client
        if not self.discord_client.is_closed():
            await self.discord_client.close()

        logger.info("Modular server stopped")
