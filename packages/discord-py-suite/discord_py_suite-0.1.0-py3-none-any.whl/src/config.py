"""Configuration management for Discord-Py-Suite."""

import os
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class Config(BaseModel):
    """Configuration for Discord-Py-Suite."""

    # Discord settings
    discord_token: Optional[str] = Field(default=None)

    # Security settings (from discord-mcp-rest)
    allow_guild_ids: List[str] = Field(default_factory=list)
    allow_channel_ids: List[str] = Field(default_factory=list)
    default_allowed_mentions: str = Field(default="none")

    # Transport settings (from mcp-discord-forum)
    transport: str = Field(default="stdio")  # "stdio" or "http"
    http_port: int = Field(default=8000)
    host: str = Field(default="localhost")

    # Gateway settings (from discord-mcp-rest)
    gateway_intents: int = Field(default=513)  # Guilds + Guild Messages
    enable_gateway: bool = Field(default=True)

    # Pack system (from discord-mcp-rest)
    pack_core: bool = Field(default=True)  # Always enabled
    pack_admin: bool = Field(default=True)
    pack_media: bool = Field(default=True)
    pack_community: bool = Field(default=True)
    pack_devtools: bool = Field(default=False)

    # Health monitoring (from mcp-discord-forum)
    health_check_enabled: bool = Field(default=True)
    config_endpoint_enabled: bool = Field(default=True)

    # Auto-generation (from discord-mcp-rest)
    enable_auto_generation: bool = Field(default=True)
    route_catalog_path: str = Field(default="catalog/discord_routes.json")

    # Route handling (enhanced from discord-mcp-rest)
    enable_route_handling: bool = Field(default=True)
    enable_webhook_routes: bool = Field(default=True)
    enable_guild_routes: bool = Field(default=True)
    enable_channel_routes: bool = Field(default=True)
    route_timeout: int = Field(default=30)  # seconds
    max_route_payload_size: int = Field(default=1024 * 1024)  # 1MB

    # Feature flags (legacy from mcp-discord-forum)
    enable_user_management: bool = Field(default=True)
    enable_voice_channels: bool = Field(default=True)
    enable_direct_messages: bool = Field(default=True)
    enable_server_management: bool = Field(default=True)
    enable_rbac: bool = Field(default=True)
    enable_content_management: bool = Field(default=True)

    # Logging and debug
    debug: bool = Field(default=False)
    log_level: str = Field(default="INFO")

    # Legacy port for backward compatibility
    port: int = Field(default=8000)

    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables."""

        def parse_env_list(var_name: str) -> List[str]:
            """Parse comma-separated environment variable into list."""
            value = os.getenv(var_name, "")
            return [item.strip() for item in value.split(",") if item.strip()]

        def parse_bool(var_name: str, default: bool = True) -> bool:
            """Parse boolean environment variable."""
            value = os.getenv(var_name, str(default))
            return value.lower() in ("true", "1", "yes", "on")

        return cls(
            # Discord settings
            discord_token=os.getenv("DISCORD_BOT_TOKEN") or os.getenv("DISCORD_TOKEN"),
            # Security settings
            allow_guild_ids=parse_env_list("ALLOW_GUILD_IDS"),
            allow_channel_ids=parse_env_list("ALLOW_CHANNEL_IDS"),
            default_allowed_mentions=os.getenv("ALLOWED_MENTIONS", "none"),
            # Transport settings
            transport=os.getenv("TRANSPORT", "stdio"),
            http_port=int(os.getenv("HTTP_PORT", "8000")),
            host=os.getenv("HOST", "localhost"),
            port=int(os.getenv("PORT", "8000")),  # Legacy
            # Gateway settings
            gateway_intents=int(os.getenv("GATEWAY_INTENTS", "513")),
            enable_gateway=parse_bool("ENABLE_GATEWAY", True),
            # Pack system
            pack_core=True,  # Always enabled
            pack_admin=parse_bool("PACK_ADMIN"),
            pack_media=parse_bool("PACK_MEDIA"),
            pack_community=parse_bool("PACK_COMMUNITY"),
            pack_devtools=parse_bool("PACK_DEVTOOLS", False),
            # Health monitoring
            health_check_enabled=parse_bool("HEALTH_CHECK_ENABLED"),
            config_endpoint_enabled=parse_bool("CONFIG_ENDPOINT_ENABLED"),
            # Auto-generation
            enable_auto_generation=parse_bool("ENABLE_AUTO_GENERATION"),
            route_catalog_path=os.getenv(
                "ROUTE_CATALOG_PATH", "catalog/discord_routes.json"
            ),
            # Route handling
            enable_route_handling=parse_bool("ENABLE_ROUTE_HANDLING", True),
            enable_webhook_routes=parse_bool("ENABLE_WEBHOOK_ROUTES", True),
            enable_guild_routes=parse_bool("ENABLE_GUILD_ROUTES", True),
            enable_channel_routes=parse_bool("ENABLE_CHANNEL_ROUTES", True),
            route_timeout=int(os.getenv("ROUTE_TIMEOUT", "30")),
            max_route_payload_size=int(
                os.getenv("MAX_ROUTE_PAYLOAD_SIZE", str(1024 * 1024))
            ),
            # Feature flags (legacy)
            enable_user_management=parse_bool("ENABLE_USER_MANAGEMENT"),
            enable_voice_channels=parse_bool("ENABLE_VOICE_CHANNELS"),
            enable_direct_messages=parse_bool("ENABLE_DIRECT_MESSAGES"),
            enable_server_management=parse_bool("ENABLE_SERVER_MANAGEMENT"),
            enable_rbac=parse_bool("ENABLE_RBAC"),
            enable_content_management=parse_bool("ENABLE_CONTENT_MANAGEMENT"),
            # Logging and debug
            debug=parse_bool("DEBUG", False),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
        )

    def is_configured(self) -> bool:
        """Check if the minimum required configuration is present."""
        return self.discord_token is not None

    def get_missing_requirements(self) -> List[str]:
        """Get list of missing required configuration items."""
        missing = []
        if not self.discord_token:
            missing.append("DISCORD_BOT_TOKEN or DISCORD_TOKEN")
        return missing

    def get_health_status(self) -> Dict[str, Any]:
        """Get health status information."""
        status = "healthy"
        checks = {}

        # Check Discord token
        if self.discord_token:
            checks["discord_token"] = "configured"
        else:
            checks["discord_token"] = "missing"
            status = "unhealthy"

        # Check environment
        checks["environment"] = "loaded"

        return {
            "status": status,
            "checks": checks,
            "details": {
                "features_enabled": {
                    "user_management": self.enable_user_management,
                    "voice_channels": self.enable_voice_channels,
                    "direct_messages": self.enable_direct_messages,
                    "server_management": self.enable_server_management,
                    "rbac": self.enable_rbac,
                    "content_management": self.enable_content_management,
                    "route_handling": self.enable_route_handling,
                    "webhook_routes": self.enable_webhook_routes,
                    "guild_routes": self.enable_guild_routes,
                    "channel_routes": self.enable_channel_routes,
                },
                "packs_enabled": {
                    "admin": self.pack_admin,
                    "media": self.pack_media,
                    "community": self.pack_community,
                    "devtools": self.pack_devtools,
                },
                "security": {
                    "guild_allowlist": len(self.allow_guild_ids) > 0,
                    "channel_allowlist": len(self.allow_channel_ids) > 0,
                    "allowed_guilds_count": len(self.allow_guild_ids),
                    "allowed_channels_count": len(self.allow_channel_ids),
                },
            },
        }
