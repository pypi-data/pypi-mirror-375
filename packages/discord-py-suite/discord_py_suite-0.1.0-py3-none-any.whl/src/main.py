"""Main entry point for Discord-Py-Suite."""

import asyncio
import sys
from pathlib import Path
from typing import Any
import discord
from dotenv import load_dotenv
from loguru import logger

from .config import Config
from .server import DiscordMCPServer


def setup_logging(config: Config) -> None:
    """Set up logging configuration."""
    logger.remove()  # Remove default handler

    # Add console handler with colored output
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=config.log_level,
        colorize=True,
    )

    if config.debug:
        logger.add(
            "discord-py-suite.log",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level="DEBUG",
            rotation="1 day",
            retention="7 days",
        )


async def create_discord_client(config: Config) -> discord.Client:
    """Create and configure Discord client."""
    intents = discord.Intents.default()
    intents.message_content = True
    intents.guilds = True
    intents.guild_messages = True
    intents.guild_reactions = True
    intents.members = True  # For user management features
    intents.voice_states = True  # For voice channel features

    client = discord.Client(intents=intents)

    @client.event
    async def on_ready() -> None:
        logger.info(f"Discord client logged in as {client.user}")
        logger.info(f"Connected to {len(client.guilds)} guilds")

    @client.event
    async def on_error(event: str, *args: Any, **kwargs: Any) -> None:
        logger.error(f"Discord client error in {event}: {args}")

    return client


async def main_async() -> None:
    """Main async entry point."""
    # Load environment variables
    load_dotenv()

    # Load configuration
    config = Config.from_env()

    # Set up logging
    setup_logging(config)

    logger.info("Starting Discord-Py-Suite...")
    from . import __version__

    logger.info(f"Version: {__version__}")

    # Check configuration
    if not config.is_configured():
        missing = config.get_missing_requirements()
        logger.error(f"Missing required configuration: {', '.join(missing)}")
        logger.info("Please check your environment variables or .env file")
        sys.exit(1)

    # Create Discord client
    client = await create_discord_client(config)

    # Create and start MCP server
    mcp_server = DiscordMCPServer(client, config)

    logger.info(f"Starting MCP server on {config.host}:{config.port}")

    try:
        await mcp_server.start()
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down...")
    except Exception as e:
        logger.error(f"Error starting MCP server: {e}")
        sys.exit(1)
    finally:
        await mcp_server.stop()
        if not client.is_closed():
            await client.close()


def main() -> None:
    """Main entry point."""
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        logger.info("Shutdown complete")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
