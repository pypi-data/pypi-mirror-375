#!/usr/bin/env python3
"""Entry point for Discord MCP Server."""

import asyncio
import os
import sys
from pathlib import Path

# Add the src directory to Python path
src_dir = Path(__file__).parent
sys.path.insert(0, str(src_dir))

try:
    from main import main
except ImportError as e:
    print(f"Import error: {e}")
    print("Available files in src:", os.listdir(src_dir))
    sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())