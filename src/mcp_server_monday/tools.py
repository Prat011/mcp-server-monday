import json
import logging
from enum import Enum
from typing import Optional, Sequence, Union

import mcp.types as types
from mcp.server import Server
from monday import MondayClient

from mcp_server_monday.constants import MONDAY_WORKSPACE_URL

logger = logging.getLogger("mcp-server-monday")


class ToolName(str, Enum):
    CREATE_ITEM = "monday-create-item"
    GET_BOARD_GROUPS = "monday-get-board-groups"
    CREATE_UPDATE = "monday-create-update"
    LIST_BOARDS = "monday-list-boards"
    LIST_ITEMS_IN_GROUPS = "monday-list-items-in-groups"
    LIST_SUBITEMS_IN_ITEMS = "monday-list-subitems-in-items"
    GET_BOARD_COLUMNS = "monday-get-board-columns"


ServerTools = [
    types.Tool(
        name=ToolName.CREATE_ITEM,
        description="Create a new item in a Monday.com Board. Optionally, specify the parent Item ID to create a Sub-item.",
        inputSchema={
            "type": "object",
            "properties": {
                "boardId": {"type": "string"},
                "itemTitle": {"type": "string"},
                "groupId": {
                    "type": "string",
                    "description": "If set, parentItemId should not be set.",
                },
                "parentItemId": {
                    "type": "string",
                    "description": "If set, groupId should not be set.",
                },
                "column_values": {
                    "type": "object",
                    "description": "Dictionary of column values to set {column_id: value}",
                },
            },
            "required": ["boardId", "itemTitle"],
        },
    ),
    types.Tool(
        name=ToolName.GET_BOARD_COLUMNS,
        description="Get the Columns of a Monday.com Board.",
        inputSchema={
            "type": "object",
            "properties": {
                "boardId": {"type": "string"},
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
                "boardId": {"type": "string"},
            },
            "required": ["boardId"],
        },
    ),
    types.Tool(
        name=ToolName.CREATE_UPDATE,
        description="Create an update (comment) on a Monday.com item",
        inputSchema={
            "type": "object",
            "properties": {
                "itemId": {"type": "string"},
                "updateText": {"type": "string"},
            },
            "required": ["itemId", "updateText"],
        },
    ),
    types.Tool(
        name=ToolName.LIST_BOARDS,
        description="Get all boards from Monday.com",
        inputSchema={
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of boards to return",
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
                "boardId": {"type": "string"},
                "groupIds": {"type": "array", "items": {"type": "string"}},
                "limit": {"type": "integer"},
                "cursor": {"type": "string"},
            },
            "required": ["boardId", "groupIds"],
        },
    ),
    types.Tool(
        name=ToolName.LIST_SUBITEMS_IN_ITEMS,
        description="List all Sub-items of a list of Monday Items",
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
                    return handle_monday_create_item(
                        boardId=arguments.get("boardId"),
                        itemTitle=arguments.get("itemTitle"),
                        groupId=arguments.get("groupId"),
                        parentItemId=arguments.get("parentItemId"),
                        column_values=arguments.get("column_values"),
                        monday_client=monday_client,
                    )
                case ToolName.GET_BOARD_COLUMNS:
                    return handle_monday_get_board_columns(
                        boardId=arguments.get("boardId"), monday_client=monday_client
                    )
                case ToolName.GET_BOARD_GROUPS:
                    return handle_monday_get_board_groups(
                        boardId=arguments.get("boardId"), monday_client=monday_client
                    )

                case ToolName.CREATE_UPDATE:
                    return handle_monday_create_update(
                        itemId=arguments.get("itemId"),
                        updateText=arguments.get("updateText"),
                        monday_client=monday_client,
                    )

                case ToolName.LIST_BOARDS:
                    return handle_monday_list_boards(monday_client=monday_client)

                case ToolName.LIST_ITEMS_IN_GROUPS:
                    return handle_monday_list_items_in_groups(
                        boardId=arguments.get("boardId"),
                        groupIds=arguments.get("groupIds"),
                        limit=arguments.get("limit"),
                        cursor=arguments.get("cursor"),
                        monday_client=monday_client,
                    )

                case ToolName.LIST_SUBITEMS_IN_ITEMS:
                    return handle_monday_list_subitems_in_items(
                        itemIds=arguments.get("itemIds"), monday_client=monday_client
                    )

                case _:
                    raise ValueError(f"Undefined behaviour for tool: {name}")

        except Exception as e:
            logger.error(f"Error calling tool {name}: {e}")
            raise


def handle_monday_create_item(
    boardId: str,
    itemTitle: str,
    monday_client: MondayClient,
    groupId: Optional[str] = None,
    parentItemId: Optional[str] = None,
    column_values: Optional[dict] = None,
) -> list[types.TextContent]:
    """Create a new item in a Monday.com Board. Optionally, specify the parent Item ID to create a Sub-item."""
    if parentItemId is None and groupId is not None:
        response = monday_client.items.create_item(
            board_id=boardId,
            group_id=groupId,
            item_name=itemTitle,
            column_values=column_values,
        )
    elif parentItemId is not None and groupId is None:
        response = monday_client.items.create_subitem(
            parent_item_id=parentItemId,
            subitem_name=itemTitle,
            column_values=column_values,
        )
    else:
        return [
            types.TextContent(
                type="text",
                text="You can set either groupId or parentItemId argument, but not both.",
            )
        ]

    try:
        data = response["data"]
        id_key = "create_item" if parentItemId is None else "create_subitem"
        item_url = f"{MONDAY_WORKSPACE_URL}/boards/{boardId}/pulses/{data.get(id_key).get('id')}"
        return [
            types.TextContent(
                type="text",
                text=f"Created a new Monday item. URL: {item_url}",
            )
        ]
    except Exception as e:
        return [
            types.TextContent(
                type="text",
                text=f"Error creating Monday item: {e}",
            )
        ]


def handle_monday_get_board_groups(
    boardId: str, monday_client: MondayClient
) -> list[types.TextContent]:
    """Get the Groups of a Monday.com Board."""
    response = monday_client.groups.get_groups_by_board(board_ids=boardId)
    return [
        types.TextContent(
            type="text",
            text=f"Got the groups of a Monday board. {json.dumps(response['data'])}",
        )
    ]


def handle_monday_get_board_columns(
    boardId: str, monday_client: MondayClient
) -> list[types.TextContent]:
    """Get the Columns of a Monday.com Board."""
    query = f"""
        query {{
            boards(ids: {boardId}) {{
                columns {{
                    id
                    title
                    type
                }}
            }}
        }}
    """
    response = monday_client.custom._query(query)
    return [
        types.TextContent(
            type="text",
            text=f"Got the columns of a Monday board. {json.dumps(response)}",
        )
    ]


def handle_monday_create_update(
    itemId: str,
    updateText: str,
    monday_client: MondayClient,
) -> list[types.TextContent]:
    """Create an update (comment) on a Monday.com item."""
    monday_client.updates.create_update(item_id=itemId, update_value=updateText)
    return [
        types.TextContent(
            type="text", text=f"Created new update on Monday item: {updateText}"
        )
    ]


def handle_monday_list_boards(
    monday_client: MondayClient, limit: int = 100
) -> list[types.TextContent]:
    """List all available Monday.com boards"""
    response = monday_client.boards.fetch_boards(limit=limit)
    boards = response["data"]["boards"]

    board_list = "\n".join(
        [f"- {board['name']} (ID: {board['id']})" for board in boards]
    )

    return [
        types.TextContent(
            type="text", text=f"Available Monday.com Boards:\n{board_list}"
        )
    ]


def handle_monday_list_items_in_groups(
    boardId: str,
    groupIds: list[str],
    monday_client: MondayClient,
    limit: int = 100,
    cursor: Optional[str] = None,
) -> list[types.TextContent]:
    """List all items in the specified groups of a Monday.com board"""

    if groupIds and not cursor:
        formatted_group_ids = ", ".join([f'"{group_id}"' for group_id in groupIds])
        items_page_params = f"""
            query_params: {{
                rules: [
                    {{column_id: "group", compare_value: [{formatted_group_ids}], operator: any_of}}
                ]
            }}
        """
    else:
        items_page_params = f'cursor: "{cursor}"'

    items_page_params += f" limit: {limit}"
    query = f"""
    query {{
        boards (ids: {boardId}) {{
            items_page ({items_page_params}) {{
                cursor
                items {{
                    id
                    name
                    column_values {{
                        id
                        text
                        value
                    }}
                }}
            }}
        }}
    }}
    """

    response = monday_client.custom._query(query)
    return [
        types.TextContent(
            type="text",
            text=f"Items in groups {groupIds} of Monday board {boardId}: {json.dumps(response)}",
        )
    ]


def handle_monday_list_subitems_in_items(
    itemIds: list[str],
    monday_client: MondayClient,
) -> list[types.TextContent]:
    formatted_item_ids = ", ".join(itemIds)
    get_subitems_in_item_query = f"""query
        {{
            items ([{formatted_item_ids}]) {{
                subitems {{
                    id
                    name
                    parent_item {{
                        id
                    }}
                    column_values {{
                        id
                        text
                        value
                    }}
                }}
            }}
        }}"""
    response = monday_client.custom._query(get_subitems_in_item_query)

    return [
        types.TextContent(
            type="text",
            text=f"Sub-items of Monday items {itemIds}: {json.dumps(response)}",
        )
    ]
