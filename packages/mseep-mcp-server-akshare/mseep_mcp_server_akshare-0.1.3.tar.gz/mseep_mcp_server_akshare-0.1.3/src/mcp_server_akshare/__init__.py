"""
MCP server for AKShare financial data.
"""

import asyncio
import logging
from typing import Optional

from .server import main as server_main

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def main() -> None:
    """
    Main entry point for the AKShare MCP server.
    """
    logger.info("Starting AKShare MCP server...")
    try:
        await server_main()
    except Exception as e:
        logger.error(f"Error running AKShare MCP server: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    asyncio.run(main()) 