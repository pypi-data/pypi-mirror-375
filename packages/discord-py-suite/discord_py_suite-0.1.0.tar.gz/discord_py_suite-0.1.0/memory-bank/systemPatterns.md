# Discord-Py-Suite System Patterns

## Architectural Framework
- **FastMCP Framework**: Modern MCP implementation providing type-safe server-side tools with automatic schema generation
- **Modular Design**: Single responsibility principle with separate modules for different Discord API domains
- **Decorator Pattern**: `@app.tool()` decorators for clean, declarative tool registration
- **Class-Based Server**: `DiscordMCPServer` class encapsulating Discord client, configuration, and tool setup

## Core Design Patterns

### Service Locator Pattern
- Tool registration functions imported and called centrally in `server.py`
- Each tool module exports a registration function: `register_{module}_tools(app, client, config)`
- Consistent parameter signature across all tool categories

### Error Handling Pattern
- Try/catch blocks in all Discord operations with Discord-specific exception handling
- Standardized response format: `{"success": True, "data": {...}}` or `{"success": False, "error": "..."}`
- Logging of errors with appropriate levels (info, error, warning)

### Permission Checking Pattern
```python
bot_member = guild.get_member(client.user.id) if client.user else None
if not bot_member or not bot_member.guild_permissions.{permission}:
    return {"success": False, "error": "Bot lacks {permission} permission"}
```

### Async Operation Pattern
- All Discord API operations are async/await based
- Event-driven Discord client with proper event loop management
- Long-running operations handled in background tasks

## Tool Organization Patterns

### Module Structure
Each tool module follows:
```python
# src/tools/{domain}.py
from typing import Dict, Any, Optional
import discord
import logging
from mcp import FastMCP

logger = logging.getLogger(__name__)

def register_{domain}_tools(app: FastMCP, client: discord.Client, config) -> None:
    # Tool definitions with @app.tool() decorators
```

### Tool Function Pattern
```python
@app.tool()
async def discord_{operation_name}(param: Type, optional: Optional[Type] = None) -> Dict[str, Any]:
    """Tool description with clear parameters and return value documentation."""
    try:
        # Permission checking
        # Discord operation
        # Result formatting
        return {"success": True, "data": formatted_result}
    except discord.Forbidden:
        return {"success": False, "error": "Bot lacks required permissions"}
    # Other exception handling
```

## Configuration Pattern
- **Pydantic Models**: Type-safe configuration validation with automatic environment variable parsing
- **Late Binding**: Discord client initialized after configuration validation
- **Missing Requirements**: Automatic detection and reporting of missing configuration (e.g., Discord token)

## Testing Patterns
- **AsyncIO Testing**: Pytest with asyncio support for concurrent operations
- **Mock Objects**: Discord-specific mocks for unit testing
- **Integration Tests**: End-to-end tool functionality testing

## Deployment Patterns

### Environment-Based Configuration
- Different transport protocols selectable via environment variables
- Host/port binding for HTTP/WebSocket servers
- Logging level configuration for production vs development

### Process Management
- Clean startup/shutdown with proper resource cleanup
- Background process execution for development testing
- Graceful error handling with proper exit codes

## Security Patterns

### Discord Permission Checking
- Bot permission verification before operations
- Role hierarchy validation for moderation actions
- Safe operation boundaries to prevent abuse

### Input Validation
- Type hints enforced by FastMCP framework
- Parameter validation through Pydantic models
- Safe string handling for user-generated content

## Extensibility Patterns

### New Tool Addition
1. Create new module in `src/tools/` under 400 lines
2. Implement registration function with consistent signature
3. Add registration call to `server.py`
4. Update documentation and export in `__init__.py`

### Framework Usage
- Leverage FastMCP's automatic schema generation from type hints
- Follow established error handling and permission patterns
- Maintain consistent naming conventions (`discord_{action}`)

## Performance Patterns

### Connection Management
- Persistent Discord client with connection pooling
- Efficient event handling with focused intents
- Rate limit compliance with exponential backoff if needed

### Memory Efficiency
- Minimal global state and singleton patterns
- Garbage collection friendly async operations
- Stream processing for large message histories

## Monitoring and Observability
- **Loguru Integration**: Structured logging with JSON output in production
- **Health Check Endpoints**: Built-in status monitoring for long-running processes
- **Debug Logging**: Development-friendly verbose output with sensitive data filtering

## Phase 2 Architectural Achievements
- **Expanded Module Structure**: From 5 to 8 tool categories (56 total tools)
- **Role Management**: Complete role lifecycle with permissions and hierarchy
- **Voice Channel Administration**: Full voice management with user controls
- **Webhook Integration**: Complete webhook lifecycle and message routing
- **Advanced Moderation**: Expanded from basic to comprehensive moderation suite
- **Architecture Scalability**: Successfully handled tool count growth without degradation
- **Performance Optimization**: All new tools maintain consistent response times and resource usage
- **Type Safety**: Full typing coverage maintained across all new implementations
- **Error Handling**: Standardized error patterns applied to all new tool categories
- **Documentation**: Comprehensive docstrings and usage examples for all new tools