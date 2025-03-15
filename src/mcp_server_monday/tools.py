import logging
from enum import Enum
from typing import Sequence, Union

import mcp.types as types
from mcp.server import Server
from monday import MondayClient

from mcp_server_monday.board import (
    handle_monday_get_board_columns,
    handle_monday_get_board_groups,
    handle_monday_list_boards,
)
from mcp_server_monday.item import (
    handle_monday_create_item,
    handle_monday_create_update_on_item,
    handle_monday_get_item_by_id,
    handle_monday_list_items_in_groups,
    handle_monday_list_subitems_in_items,
    handle_monday_update_item,
)

logger = logging.getLogger("mcp-server-monday")


class ToolName(str, Enum):
    LIST_BOARDS = "monday-list-boards"
    GET_BOARD_GROUPS = "monday-get-board-groups"
    GET_BOARD_COLUMNS = "monday-get-board-columns"

    CREATE_ITEM = "monday-create-item"
    UPDATE_ITEM = "monday-update-item"
    CREATE_UPDATE = "monday-create-update"
    LIST_ITEMS_IN_GROUPS = "monday-list-items-in-groups"
    LIST_SUBITEMS_IN_ITEMS = "monday-list-subitems-in-items"
    GET_ITEM_BY_ID = "monday-get-items-by-id"


ServerTools = [
    types.Tool(
        name=ToolName.CREATE_ITEM,
        description="Create a new item in a Monday.com Board. Optionally, specify the parent Item ID to create a Sub-item.",
        inputSchema={
            "type": "object",
            "properties": {
                "boardId": {
                    "type": "string",
                    "description": "Monday.com Board ID that the Item or Sub-item is on.",
                },
                "itemTitle": {
                    "type": "string",
                    "description": "Name of the Monday.com Item or Sub-item that will be created.",
                },
                "groupId": {
                    "type": "string",
                    "description": "Monday.com Board's Group ID to create the Item in. If set, parentItemId should not be set.",
                },
                "parentItemId": {
                    "type": "string",
                    "description": "Monday.com Item ID to create the Sub-item under. If set, groupId should not be set.",
                },
                "columnValues": {
                    "type": "object",
                    "description": "Dictionary of column values to set {column_id: value}",
                },
            },
            "required": ["boardId", "itemTitle"],
        },
    ),
    types.Tool(
        name=ToolName.GET_ITEM_BY_ID,
        description="Fetch specific Monday.com item by its ID",
        inputSchema={
            "type": "object",
            "properties": {
                "itemId": {
                    "type": "string",
                    "description": "ID of the Monday.com item to fetch.",
                },
            },
            "required": ["itemId"],
        },
    ),
    types.Tool(
        name=ToolName.UPDATE_ITEM,
        description="Update a Monday.com item's or sub-item's column values.",
        inputSchema={
            "type": "object",
            "properties": {
                "boardId": {
                    "type": "string",
                    "description": "Monday.com Board ID that the Item or Sub-item is on.",
                },
                "itemId": {
                    "type": "string",
                    "description": "Monday.com Item or Sub-item ID to update the columns of.",
                },
                "columnValues": {
                    "type": "object",
                    "description": "Dictionary of column values to update the Monday.com Item or Sub-item with. ({column_id: value})",
                },
            },
            "required": ["boardId", "itemId", "columnValues"],
        },
    ),
    types.Tool(
        name=ToolName.GET_BOARD_COLUMNS,
        description="Get the Columns of a Monday.com Board.",
        inputSchema={
            "type": "object",
            "properties": {
                "boardId": {
                    "type": "string",
                    "description": "Monday.com Board ID that the Item or Sub-item is on.",
                },
            },
            "required": ["boardId"],
        },
    ),
    types.Tool(
        name=ToolName.GET_BOARD_GROUPS,
        description="Get the Groups of a Monday.com Board.",
        inputSchema={
            "type": "object",
            "properties": {
                "boardId": {
                    "type": "string",
                    "description": "Monday.com Board ID that the Item or Sub-item is on.",
                },
            },
            "required": ["boardId"],
        },
    ),
    types.Tool(
        name=ToolName.CREATE_UPDATE,
        description="Create an update (comment) on a Monday.com Item or Sub-item.",
        inputSchema={
            "type": "object",
            "properties": {
                "itemId": {"type": "string"},
                "updateText": {
                    "type": "string",
                    "description": "Content to update the Item or Sub-item with.",
                },
            },
            "required": ["itemId", "updateText"],
        },
    ),
    types.Tool(
        name=ToolName.LIST_BOARDS,
        description="Get all Boards from Monday.com",
        inputSchema={
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of Monday.com Boards to return.",
                }
            },
        },
    ),
    types.Tool(
        name=ToolName.LIST_ITEMS_IN_GROUPS,
        description="List all items in the specified groups of a Monday.com board",
        inputSchema={
            "type": "object",
            "properties": {
                "boardId": {
                    "type": "string",
                    "description": "Monday.com Board ID that the Item or Sub-item is on.",
                },
                "groupIds": {"type": "array", "items": {"type": "string"}},
                "limit": {"type": "integer"},
                "cursor": {"type": "string"},
            },
            "required": ["boardId", "groupIds"],
        },
    ),
    types.Tool(
        name=ToolName.LIST_SUBITEMS_IN_ITEMS,
        description="List all Sub-items of a list of Monday.com Items",
        inputSchema={
            "type": "object",
            "properties": {
                "itemIds": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["itemIds"],
        },
    ),
]


def register_tools(server: Server, monday_client: MondayClient) -> None:
    @server.list_tools()
    async def handle_list_tools() -> list[types.Tool]:
        return ServerTools

    @server.call_tool()
    async def handle_call_tool(
        name: str, arguments: dict | None
    ) -> Sequence[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
        try:
            match name:
                case ToolName.CREATE_ITEM:
                    return await handle_monday_create_item(
                        boardId=arguments.get("boardId"),
                        itemTitle=arguments.get("itemTitle"),
                        groupId=arguments.get("groupId"),
                        parentItemId=arguments.get("parentItemId"),
                        columnValues=arguments.get("columnValues"),
                        monday_client=monday_client,
                    )
                case ToolName.GET_BOARD_COLUMNS:
                    return await handle_monday_get_board_columns(
                        boardId=arguments.get("boardId"), monday_client=monday_client
                    )
                case ToolName.GET_BOARD_GROUPS:
                    return await handle_monday_get_board_groups(
                        boardId=arguments.get("boardId"), monday_client=monday_client
                    )

                case ToolName.CREATE_UPDATE:
                    return await handle_monday_create_update_on_item(
                        itemId=arguments.get("itemId"),
                        updateText=arguments.get("updateText"),
                        monday_client=monday_client,
                    )

                case ToolName.UPDATE_ITEM:
                    return await handle_monday_update_item(
                        boardId=arguments.get("boardId"),
                        itemId=arguments.get("itemId"),
                        columnValues=arguments.get("columnValues"),
                        monday_client=monday_client,
                    )

                case ToolName.LIST_BOARDS:
                    return await handle_monday_list_boards(monday_client=monday_client)

                case ToolName.LIST_ITEMS_IN_GROUPS:
                    return await handle_monday_list_items_in_groups(
                        boardId=arguments.get("boardId"),
                        groupIds=arguments.get("groupIds"),
                        limit=arguments.get("limit"),
                        cursor=arguments.get("cursor"),
                        monday_client=monday_client,
                    )

                case ToolName.LIST_SUBITEMS_IN_ITEMS:
                    return await handle_monday_list_subitems_in_items(
                        itemIds=arguments.get("itemIds"), monday_client=monday_client
                    )

                case ToolName.GET_ITEMS_BY_ID:
                    return await handle_monday_get_item_by_id(
                        itemIds=arguments.get("itemId"), monday_client=monday_client
                    )
                case _:
                    raise ValueError(f"Undefined behaviour for tool: {name}")

        except Exception as e:
            logger.error(f"Error calling tool {name}: {e}")
            raise
