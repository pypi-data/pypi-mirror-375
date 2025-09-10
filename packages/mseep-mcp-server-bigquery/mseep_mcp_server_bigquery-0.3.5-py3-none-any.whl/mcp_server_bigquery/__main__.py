#!/usr/bin/env python
"""
Main entry point for the BigQuery MCP server when run as a module.
"""

import asyncio
import sys
import os
from . import main

if __name__ == "__main__":
    # Call main with no arguments
    asyncio.run(main())
