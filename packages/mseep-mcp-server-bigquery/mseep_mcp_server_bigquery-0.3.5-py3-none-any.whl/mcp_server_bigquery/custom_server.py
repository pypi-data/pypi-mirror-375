"""
Custom server implementation to avoid asyncio conflicts.
"""

import asyncio
import sys
import os
from typing import Any, Dict, List, Optional, Union
import logfire
from mcp.server.fastmcp import FastMCP
from mcp.server.stdio import stdio_server


class CustomFastMCP(FastMCP):
    """Custom FastMCP server that avoids asyncio conflicts."""

    def run(self):
        """Run the server using stdio transport without anyio.run."""
        logfire.info("Running custom server implementation")

        # Get the current event loop
        loop = asyncio.get_event_loop()

        # Use the stdio_server function to create a server
        async def run_server():
            async with stdio_server(self) as server:
                # Keep the server running
                await asyncio.Future()

        try:
            # Run the server
            loop.run_until_complete(run_server())
            logfire.info("Server connected to transport")
        except KeyboardInterrupt:
            logfire.info("Server stopped by user")
