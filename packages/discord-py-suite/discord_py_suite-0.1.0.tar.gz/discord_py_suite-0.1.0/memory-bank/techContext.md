# Discord-Py-Suite Technology Context

## Core Framework
- **FastMCP 2.12.0+**: Modern MCP implementation providing automatic schema generation, type validation, and multiple transport protocols (STDIO, HTTP, SSE)
- **Python 3.11+**: Core language with async/await support, comprehensive type hints, and modern features
- **discord.py 2.3+**: Official Python Discord API wrapper with full Discord Gateway and API support

## Development Tools
- **Package Manager**: uv 0.1+ (modern Python package management, alternative to pip/poetry)
- **Build System**: Hatchling (modern Python build backend, replaces setuptools)
- **Type Checker**: MyPy 1.8+ (static type checking for Python)
- **Formatter**: Black 23+ (Python code formatter, 88 character line length)
- **Linter**: Ruff 0.1+ (fast Python linter with security rules, some ignored: S101, S603, S607)
- **Testing Framework**: pytest with asyncio support (async operation testing)

## Core Dependencies
- **pydantic 2.5+**: Data validation and settings management with Python 3.11 type support
- **loguru 0.7+**: Structured logging with JSON output and colorful console formatting
- **uvloop**: Optional high-performance async event loop (if available)

## Configuration
- **Environment Variables**: Standard `.env` file support for token, transport, and debug settings
- **Required**: `DISCORD_BOT_TOKEN` (mandatory)
- **Optional**: `TRANSPORT`, `HOST`, `PORT`, `LOG_LEVEL`

## Transport Protocols
- **STDIO**: Standard input/output for MCP clients (Claude Desktop compatibility)
- **HTTP**: REST API server mode for web-based integrations
- **SSE**: Server-Sent Events for real-time web applications

## Development Environment Setup

### Prerequisites
- Python 3.11 or higher
- uv package manager installed
- Valid Discord bot token with appropriate server permissions

### Installation Commands
```bash
# Install dependencies
uv sync

# Development server
make run-dev

# Background testing
make mcp-test

# Configuration template
make env-template
```

## Quality Assurance
- **Static Analysis**: MyPy strict mode for type safety
- **Code Quality**: Ruff with custom rules (security-first linting)
- **Test Coverage**: pytest with asyncio support for comprehensive coverage
- **Import Validation**: Runtime import testing to ensure module integrity

## Production Considerations
- **Logging**: Different levels for development vs production (INFO vs DEBUG)
- **Error Handling**: Comprehensive exception catching with Discord API specifics
- **Resource Management**: Proper Discord client lifecycle and cleanup
- **Security**: Permission checking and hierarchy validation for all operations

## Architecture Compatibility
- **Modular Design**: Each tool category self-contained under 400 lines
- **Framework Independence**: Clear abstraction between FastMCP implementation and Discord operations
- **Type Safety**: Full typing coverage for automatic schema generation and development productivity

## Extensibility Framework
- **Tool Registration**: Decorator-based pattern for easy tool addition
- **Module System**: Import-based registration with consistent signatures
- **Configuration Injection**: Config objects passed to all tool modules for extensibility

## Performance Characteristics
- **Async First**: All Discord operations async/await based for non-blocking I/O
- **Connection Pooling**: Persistent Discord client with optimized connection management
- **Memory Efficient**: Minimal global state and garbage collection friendly patterns
- **Response Formatting**: Consistent JSON response structures with error handling

## Development Constraints
- **Python Version**: Must stay at 3.11+ (no newer features to ensure compatibility)
- **Framework Lock-in**: FastMCP usage requires maintenance of compatibility
- **Discord API**: Subject to Discord rate limits and API changes
- **Module Size**: Each tool module must stay under 400 lines for maintainability

## Deployment Options
- **CLI Tool**: `uv run python -m src.main` for command-line execution
- **Daemon Mode**: Background process support with proper monitoring
- **Docker**: Containerized deployment with environment variable injection
- **System Service**: Production installation with proper logging and monitoring