# Discord Python MCP Server - Makefile for uv-based development

.PHONY: help install dev run test format lint type-check clean build

# Default target
help:
	@echo "Discord Python MCP Server - uv Development Commands"
	@echo ""
	@echo "📦 Installation:"
	@echo "  install     Install dependencies with uv"
	@echo "  dev         Install with development dependencies"
	@echo ""
	@echo "🚀 Running:"
	@echo "  run         Run the MCP server"
	@echo "  run-dev     Run in development mode"
	@echo ""
	@echo "🧪 Testing & Quality:"
	@echo "  test        Run all tests"
	@echo "  test-cov    Run tests with coverage"
	@echo "  format      Format code with black"
	@echo "  lint        Run ruff linting"
	@echo "  type-check  Run mypy type checking"
	@echo "  qa          Run all quality checks (format, lint, type-check, test)"
	@echo ""
	@echo "🔧 Utilities:"
	@echo "  clean       Clean build artifacts"
	@echo "  build       Build the package"
	@echo "  tree        Show project structure"

# Installation commands
install:
	@echo "📦 Installing dependencies with uv..."
	uv sync

dev:
	@echo "📦 Installing with development dependencies..."
	uv sync --extra dev

# Running commands
run:
	@echo "🚀 Running Discord MCP Server..."
	uv run discord-py-suite

run-dev:
	@echo "🚀 Running in development mode..."
	uv run python -m src.main

# Testing commands
test:
	@echo "🧪 Running tests..."
	uv run pytest

test-cov:
	@echo "🧪 Running tests with coverage..."
	uv run pytest --cov=src --cov-report=term-missing

# Code quality commands
format:
	@echo "🎨 Formatting code with black..."
	uv run black src/

lint:
	@echo "🔍 Running ruff linting..."
	uv run ruff check src/

lint-fix:
	@echo "🔧 Running ruff with auto-fix..."
	uv run ruff check src/ --fix

type-check:
	@echo "🔍 Running mypy type checking..."
	uv run mypy src/

# Combined quality assurance
qa: format lint type-check test
	@echo "✅ All quality checks completed!"

# Utility commands
clean:
	@echo "🧹 Cleaning build artifacts..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build:
	@echo "📦 Building package..."
	uv build

tree:
	@echo "📂 Project structure:"
	tree -I '__pycache__|*.pyc|.pytest_cache|build|dist|*.egg-info|uv.lock' .

# Development workflow commands
check: lint type-check test
	@echo "✅ All checks passed!"

dev-setup: dev
	@echo "🎯 Development environment ready!"
	@echo "💡 Try 'make run-dev' to start the server"

# MCP-specific commands
mcp-test:
	@echo "🔌 Testing MCP server connection..."
	@echo "Note: Requires DISCORD_TOKEN environment variable"
	DISCORD_TOKEN="${DISCORD_TOKEN}" uv run python -m src.main &
	@echo "Server started in background. Check logs and stop with 'pkill -f src.main'"

# Environment setup
.env:
	@echo "📝 Creating .env template..."
	@echo "DISCORD_TOKEN=your_discord_bot_token_here" > .env
	@echo "MCP_TRANSPORT=stdio" >> .env
	@echo "LOG_LEVEL=INFO" >> .env
	@echo "📝 .env created! Edit with your Discord bot token."

env-template: .env

# Show current status
status:
	@echo "📊 Current project status:"
	@echo "Python version: $(shell python --version)"
	@echo "uv version: $(shell uv --version)"
	@echo "Dependencies: $(shell test -f uv.lock && echo "✅ Locked" || echo "❌ Not locked")"
	@echo "Package: $(shell test -d src && echo "✅ Source found" || echo "❌ Source missing")"