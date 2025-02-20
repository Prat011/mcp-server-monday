import asyncio

import mcp.server.stdio
import mcp.types as types
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions

from .tools import (
    TOOLS,
    handle_monday_create_item,
    handle_monday_create_update,
    handle_monday_get_board_groups,
    handle_monday_list_boards,
    handle_monday_list_items_in_groups,
    handle_monday_list_subitems_in_items,
)

server = Server("monday")


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """
    List available tools.
    Each tool specifies its arguments using JSON Schema validation.
    """
    return TOOLS


@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """
    Handle tool execution requests.
    Tools can modify server state and notify clients of changes.
    """
    if name not in [tool.name for tool in TOOLS]:
        raise ValueError(f"Unknown tool: {name}")

    match name:
        case "monday-create-item":
            return handle_monday_create_item(
                arguments.get("boardId"),
                arguments.get("itemTitle"),
                arguments.get("groupId"),
                arguments.get("parentItemId"),
            )

        case "monday-get-board-groups":
            return handle_monday_get_board_groups(arguments.get("boardId"))

        case "monday-create-update":
            return handle_monday_create_update(
                arguments.get("itemId"), arguments.get("updateText")
            )

        case "monday-list-boards":
            return handle_monday_list_boards()

        case "monday-list-items-in-groups":
            return handle_monday_list_items_in_groups(
                arguments.get("boardId"),
                arguments.get("groupIds"),
                arguments.get("limit"),
                arguments.get("cursor"),
            )

        case "monday-list-subitems-in-items":
            return handle_monday_list_subitems_in_items(
                arguments.get("itemIds"),
            )

        case _:
            raise ValueError(f"Undefined behaviour for tool: {name}")


async def main():
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="monday",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
