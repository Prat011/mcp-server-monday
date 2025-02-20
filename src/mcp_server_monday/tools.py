import json
import os
from typing import Optional

import mcp.types as types
from monday import MondayClient

MONDAY_API_BASE_URL = "https://api.monday.com/v2"
MONDAY_API_VERSION = os.getenv("MONDAY_API_VERSION", "2025-01")
MONDAY_API_KEY = os.getenv("MONDAY_API_KEY")
MONDAY_WORKSPACE_NAME = os.getenv("MONDAY_WORKSPACE_NAME")
MONDAY_WORKSPACE_URL = f"https://{MONDAY_WORKSPACE_NAME}.monday.com"

client = MondayClient(MONDAY_API_KEY)


def handle_monday_create_item(
    boardId: str,
    itemTitle: str,
    groupId: Optional[str] = None,
    parentItemId: Optional[str] = None,
) -> list[types.TextContent]:
    """Create a new item in a Monday.com Board. Optionally, specify the parent Item ID to create a Sub-item."""
    if parentItemId is None and groupId is not None:
        response = client.items.create_item(
            board_id=boardId,
            group_id=groupId,
            item_name=itemTitle,
        )
    elif parentItemId is not None and groupId is None:
        response = client.items.create_subitem(
            parent_item_id=parentItemId,
            subitem_name=itemTitle,
        )

    data = response["data"]
    item_url = f"{MONDAY_WORKSPACE_URL}/boards/{boardId}/pulses/{data.get('create_item').get('id') if parentItemId is None else data.get('create_subitem').get('id')}"
    return [
        types.TextContent(
            type="text",
            text=f"Created a new Monday {'' if parentItemId is None else 'sub-'}item. URL: {item_url}",
        )
    ]


def handle_monday_get_board_groups(boardId: str) -> list[types.TextContent]:
    """Get the Groups of a Monday.com Board."""
    response = client.groups.get_groups_by_board(board_ids=boardId)
    return [
        types.TextContent(
            type="text",
            text=f"Got the groups of a Monday board. {json.dumps(response['data'])}",
        )
    ]


def handle_monday_create_update(
    itemId: str,
    updateText: str,
) -> list[types.TextContent]:
    """Create an update (comment) on a Monday.com item."""
    client.updates.create_update(item_id=itemId, update_value=updateText)
    return [
        types.TextContent(
            type="text", text=f"Created new update on Monday item: {updateText}"
        )
    ]


def handle_monday_list_boards(limit: int = 100) -> list[types.TextContent]:
    """List all available Monday.com boards"""
    response = client.boards.fetch_boards(limit=limit)
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
    boardId: str, groupIds: list[str], limit: int = 100, cursor: Optional[str] = None
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

    response = client.custom._query(query)
    return [
        types.TextContent(
            type="text",
            text=f"Items in groups {groupIds} of Monday board {boardId}: {json.dumps(response)}",
        )
    ]


def handle_monday_list_subitems_in_items(
    itemIds: list[str],
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
    response = client.custom._query(get_subitems_in_item_query)

    return [
        types.TextContent(
            type="text",
            text=f"Sub-items of Monday items {itemIds}: {json.dumps(response)}",
        )
    ]


TOOLS = [
    types.Tool(
        name="monday-create-item",
        description="Create a new item in a Monday.com Board. Optionally, specify the parent Item ID to create a Sub-item.",
        inputSchema={
            "type": "object",
            "properties": {
                "boardId": {"type": "string"},
                "itemTitle": {"type": "string"},
                "groupId": {"type": "string"},
                "parentItemId": {"type": "string"},
            },
            "required": ["boardId", "itemTitle"],
        },
    ),
    types.Tool(
        name="monday-get-board-groups",
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
        name="monday-create-update",
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
        name="monday-list-boards",
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
        name="monday-list-items-in-groups",
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
        name="monday-list-subitems-in-items",
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
