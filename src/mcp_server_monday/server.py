import asyncio
import importlib.metadata
import logging

import mcp.server.stdio
import mcp.server.websocket
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
from monday import MondayClient

from mcp_server_monday.constants import MONDAY_API_KEY

from .tools import (
    register_tools,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-server-monday")

monday_client = None
server = Server("monday")


async def main():
    logger.info("Starting Monday.com MCP server")

    global monday_client
    monday_client = MondayClient(MONDAY_API_KEY)
    register_tools(server, monday_client)

    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="monday",
                server_version=importlib.metadata.version("mcp-server-monday"),
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
