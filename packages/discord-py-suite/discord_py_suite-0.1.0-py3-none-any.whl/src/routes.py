"""HTTP route handling for Discord MCP server."""

from typing import Any, Dict, List, Optional, Callable, Union
import re
import json
from dataclasses import dataclass
from urllib.parse import urlparse, parse_qs

from loguru import logger


@dataclass
class RouteMatch:
    """Represents a matched route with extracted parameters."""

    route: "Route"
    path_params: Dict[str, str]
    query_params: Dict[str, List[str]]
    full_path: str


@dataclass
class Route:
    """Represents an HTTP route with pattern matching."""

    path_pattern: str
    methods: List[str]
    handler: Callable
    name: Optional[str] = None
    description: Optional[str] = None

    def __post_init__(self):
        """Compile regex pattern for path matching."""
        # Convert path pattern to regex
        # e.g., "/guilds/{guild_id}/channels/{channel_id}" -> "/guilds/(?P<guild_id>[^/]+)/channels/(?P<channel_id>[^/]+)"
        pattern = re.sub(r"\{([^}]+)\}", r"(?P<\1>[^/]+)", self.path_pattern)
        self._compiled_pattern = re.compile(f"^{pattern}$")

    def matches(self, path: str, method: str) -> Optional[RouteMatch]:
        """Check if this route matches the given path and method."""
        if method.upper() not in [m.upper() for m in self.methods]:
            return None

        match = self._compiled_pattern.match(path)
        if not match:
            return None

        # Extract path parameters
        path_params = match.groupdict()

        # Parse query parameters
        parsed_url = urlparse(path)
        query_params = parse_qs(parsed_url.query)

        return RouteMatch(
            route=self,
            path_params=path_params,
            query_params=query_params,
            full_path=path,
        )


class RouteHandler:
    """Handles HTTP route processing for Discord MCP server."""

    def __init__(self):
        self.routes: List[Route] = []
        self.middlewares: List[Callable] = []

    def add_route(
        self,
        path: str,
        methods: Union[str, List[str]],
        handler: Callable,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> None:
        """Add a new route to the handler."""
        if isinstance(methods, str):
            methods = [methods]

        route = Route(
            path_pattern=path,
            methods=methods,
            handler=handler,
            name=name,
            description=description,
        )

        self.routes.append(route)
        logger.info(f"Added route: {methods} {path}")

    def add_middleware(self, middleware: Callable) -> None:
        """Add middleware to the route processing pipeline."""
        self.middlewares.append(middleware)
        logger.info(f"Added middleware: {middleware.__name__}")

    def match_route(self, path: str, method: str) -> Optional[RouteMatch]:
        """Find the first matching route for the given path and method."""
        for route in self.routes:
            match = route.matches(path, method)
            if match:
                return match
        return None

    async def handle_request(
        self,
        path: str,
        method: str,
        headers: Dict[str, str],
        body: Optional[bytes] = None,
        query_params: Optional[Dict[str, List[str]]] = None,
    ) -> Dict[str, Any]:
        """Handle an HTTP request by routing it to the appropriate handler."""
        try:
            # Find matching route
            match = self.match_route(path, method)
            if not match:
                return {
                    "status": 404,
                    "headers": {"Content-Type": "application/json"},
                    "body": json.dumps({"error": "Route not found"}).encode(),
                }

            # Apply middlewares
            request_context = {
                "path": path,
                "method": method,
                "headers": headers,
                "body": body,
                "path_params": match.path_params,
                "query_params": query_params or match.query_params,
                "route": match.route,
            }

            for middleware in self.middlewares:
                try:
                    request_context = await middleware(request_context)
                    if request_context.get("handled", False):
                        # Middleware handled the request
                        return request_context
                except Exception as e:
                    logger.error(f"Middleware error: {e}")
                    return {
                        "status": 500,
                        "headers": {"Content-Type": "application/json"},
                        "body": json.dumps({"error": "Middleware error"}).encode(),
                    }

            # Call the route handler
            try:
                response = await match.route.handler(
                    path_params=match.path_params,
                    query_params=match.query_params,
                    headers=headers,
                    body=body,
                    context=request_context,
                )

                # Ensure response has required fields
                if "status" not in response:
                    response["status"] = 200
                if "headers" not in response:
                    response["headers"] = {"Content-Type": "application/json"}
                if "body" not in response:
                    response["body"] = json.dumps(response.get("data", {})).encode()

                return response

            except Exception as e:
                logger.error(f"Route handler error: {e}")
                return {
                    "status": 500,
                    "headers": {"Content-Type": "application/json"},
                    "body": json.dumps({"error": "Handler error"}).encode(),
                }

        except Exception as e:
            logger.error(f"Request handling error: {e}")
            return {
                "status": 500,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Internal server error"}).encode(),
            }

    def get_routes_info(self) -> List[Dict[str, Any]]:
        """Get information about all registered routes."""
        return [
            {
                "path": route.path_pattern,
                "methods": route.methods,
                "name": route.name,
                "description": route.description,
            }
            for route in self.routes
        ]


# Global route handler instance
route_handler = RouteHandler()


# Discord-specific route handlers
async def handle_webhook_delivery(
    path_params: Dict[str, str],
    query_params: Dict[str, List[str]],
    headers: Dict[str, str],
    body: Optional[bytes],
    context: Dict[str, Any],
) -> Dict[str, Any]:
    """Handle Discord webhook delivery."""
    webhook_id = path_params.get("webhook_id")
    webhook_token = path_params.get("webhook_token")

    if not webhook_id or not webhook_token:
        return {"status": 400, "data": {"error": "Invalid webhook parameters"}}

    # Parse webhook payload
    try:
        if body:
            payload = json.loads(body.decode())
        else:
            payload = {}
    except json.JSONDecodeError:
        return {"status": 400, "data": {"error": "Invalid JSON payload"}}

    # Process webhook based on type
    webhook_type = payload.get("type")

    return {
        "status": 200,
        "data": {"webhook_id": webhook_id, "type": webhook_type, "processed": True},
    }


async def handle_guild_event(
    path_params: Dict[str, str],
    query_params: Dict[str, List[str]],
    headers: Dict[str, str],
    body: Optional[bytes],
    context: Dict[str, Any],
) -> Dict[str, Any]:
    """Handle guild-related events."""
    guild_id = path_params.get("guild_id")
    event_type = path_params.get("event_type")

    if not guild_id:
        return {"status": 400, "data": {"error": "Guild ID required"}}

    return {
        "status": 200,
        "data": {"guild_id": guild_id, "event_type": event_type, "processed": True},
    }


async def handle_channel_message(
    path_params: Dict[str, str],
    query_params: Dict[str, List[str]],
    headers: Dict[str, str],
    body: Optional[bytes],
    context: Dict[str, Any],
) -> Dict[str, Any]:
    """Handle channel message operations."""
    guild_id = path_params.get("guild_id")
    channel_id = path_params.get("channel_id")

    if not guild_id or not channel_id:
        return {"status": 400, "data": {"error": "Guild ID and Channel ID required"}}

    return {
        "status": 200,
        "data": {"guild_id": guild_id, "channel_id": channel_id, "processed": True},
    }


# Middleware functions
async def auth_middleware(context: Dict[str, Any]) -> Dict[str, Any]:
    """Middleware for authentication."""
    auth_header = context["headers"].get("Authorization", "")

    if not auth_header.startswith("Bot "):
        context["handled"] = True
        return {
            "status": 401,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Invalid authentication"}).encode(),
        }

    # Extract bot token
    context["bot_token"] = auth_header[4:]  # Remove "Bot " prefix
    return context


async def logging_middleware(context: Dict[str, Any]) -> Dict[str, Any]:
    """Middleware for request logging."""
    logger.info(f"Request: {context['method']} {context['path']}")
    return context


async def cors_middleware(context: Dict[str, Any]) -> Dict[str, Any]:
    """Middleware for CORS handling."""
    if context["method"] == "OPTIONS":
        context["handled"] = True
        return {
            "status": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization",
            },
            "body": b"",
        }

    # Add CORS headers to all responses
    context["cors_headers"] = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "Content-Type, Authorization",
    }

    return context


def setup_default_routes() -> None:
    """Set up default Discord-related routes."""
    # Add middlewares
    route_handler.add_middleware(logging_middleware)
    route_handler.add_middleware(cors_middleware)
    route_handler.add_middleware(auth_middleware)

    # Webhook routes
    route_handler.add_route(
        "/webhooks/{webhook_id}/{webhook_token}",
        ["POST"],
        handle_webhook_delivery,
        name="webhook_delivery",
        description="Handle Discord webhook deliveries",
    )

    # Guild event routes
    route_handler.add_route(
        "/guilds/{guild_id}/events/{event_type}",
        ["POST"],
        handle_guild_event,
        name="guild_event",
        description="Handle guild events",
    )

    # Channel message routes
    route_handler.add_route(
        "/guilds/{guild_id}/channels/{channel_id}/messages",
        ["POST", "GET"],
        handle_channel_message,
        name="channel_message",
        description="Handle channel message operations",
    )

    logger.info("Default Discord routes configured")


# Export the global route handler
__all__ = ["route_handler", "RouteHandler", "setup_default_routes"]
