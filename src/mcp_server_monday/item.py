from __future__ import annotations

import json
from typing import Optional

from mcp import types
from monday import MondayClient

from mcp_server_monday.constants import MONDAY_WORKSPACE_URL


async def handle_monday_list_items_in_groups(
    boardId: str,
    groupIds: list[str],
    limit: int,
    monday_client: MondayClient,
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
                    updates {{
                        id
                        body
                    }}
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
            text=f"Items in groups {groupIds} of Monday.com board {boardId}: {json.dumps(response)}",
        )
    ]


async def handle_monday_list_subitems_in_items(
    itemIds: list[str],
    monday_client: MondayClient,
) -> list[types.TextContent]:
    formatted_item_ids = ", ".join(itemIds)
    get_subitems_in_item_query = f"""query
        {{
            items (ids: [{formatted_item_ids}]) {{
                subitems {{
                    id
                    name
                    parent_item {{
                        id
                    }}
                    updates {{
                        id
                        body
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
            text=f"Sub-items of Monday.com items {itemIds}: {json.dumps(response)}",
        )
    ]


async def handle_monday_create_item(
    boardId: str,
    itemTitle: str,
    monday_client: MondayClient,
    groupId: Optional[str] = None,
    parentItemId: Optional[str] = None,
    columnValues: Optional[dict] = None,
) -> list[types.TextContent]:
    """Create a new item in a Monday.com Board. Optionally, specify the parent Item ID to create a Sub-item."""
    if parentItemId is None and groupId is not None:
        response = monday_client.items.create_item(
            board_id=boardId,
            group_id=groupId,
            item_name=itemTitle,
            column_values=columnValues,
        )
    elif parentItemId is not None and groupId is None:
        response = monday_client.items.create_subitem(
            parent_item_id=parentItemId,
            subitem_name=itemTitle,
            column_values=columnValues,
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
                text=f"Created a new Monday.com item. URL: {item_url}",
            )
        ]
    except Exception as e:
        return [
            types.TextContent(
                type="text",
                text=f"Error creating Monday.com item: {e}",
            )
        ]


async def handle_monday_update_item(
    boardId: str,
    itemId: str,
    columnValues: dict[str],
    monday_client: MondayClient,
):
    response = monday_client.items.change_multiple_column_values(
        board_id=boardId, item_id=itemId, column_values=columnValues
    )
    return [
        types.TextContent(
            type="text", text=f"Updated Monday.com item. {json.dumps(response)}"
        )
    ]


async def handle_monday_create_update_on_item(
    itemId: str,
    updateText: str,
    monday_client: MondayClient,
) -> list[types.TextContent]:
    monday_client.updates.create_update(item_id=itemId, update_value=updateText)
    return [
        types.TextContent(
            type="text", text=f"Created new update on Monday.com item: {updateText}"
        )
    ]


async def handle_monday_get_item_by_id(
    itemId: str,
    monday_client: MondayClient,
) -> list[types.TextContent]:
    """Fetch specific Monday.com items by their IDs"""
    try:
        response = monday_client.items.fetch_items_by_id(ids=itemId)

        return [
            types.TextContent(
                type="text",
                text=f"Monday.com items: {json.dumps(response)}",
            )
        ]
    except Exception as e:
        return [
            types.TextContent(
                type="text",
                text=f"Error fetching Monday.com items: {e}",
            )
        ]


async def handle_monday_get_item_updates(
    itemId: str,
    monday_client: MondayClient,
    limit: int = 25,
) -> list[types.TextContent]:
    """Get updates for a specific item in Monday.com"""

    query = f"""
    query {{
        items (ids: {itemId}) {{
            updates (limit: {limit}) {{
                id
                body
                created_at
                creator {{
                    id
                    name
                }}
                assets {{
                    id
                    name
                    url
                }}
            }}
        }}
    }}
    """

    # Setting no_log flag to true if it exists to prevent activity tracking
    # Note: This is a preventative measure as the _query method might accept this parameter
    try:
        response = monday_client.custom._query(query, no_log=True)
    except TypeError:
        # If no_log param doesn't exist, try with default params
        response = monday_client.custom._query(query)

    if (
        not response
        or "data" not in response
        or not response["data"]["items"]
        or not response["data"]["items"][0]["updates"]
    ):
        return [
            types.TextContent(type="text", text=f"No updates found for item {itemId}.")
        ]

    updates = response["data"]["items"][0]["updates"]

    formatted_updates = []
    for update in updates:
        update_text = f"Update ID: {update['id']}\n"
        update_text += f"Created: {update['created_at']}\n"
        update_text += (
            f"Creator: {update['creator']['name']} (ID: {update['creator']['id']})\n"
        )
        update_text += f"Body: {update['body']}\n"

        # Add information about attached files if present
        if update.get("assets"):
            update_text += "\nAttached Files:\n"
            for asset in update["assets"]:
                update_text += f"- {asset['name']}: {asset['url']}\n"

        update_text += "\n\n"
        formatted_updates.append(update_text)

    return [
        types.TextContent(
            type="text",
            text=f"Updates for item {itemId}:\n\n{''.join(formatted_updates)}",
        )
    ]


async def handle_monday_move_item_to_group(
    monday_client: MondayClient, item_id: str, group_id: str
) -> list[types.TextContent]:
    """
    Move an item to a group in a Monday.com board.

    Args:
        monday_client (MondayClient): The Monday.com client.
        item_id (str): The ID of the item to move.
        group_id (str): The ID of the group to move the item to.
    """
    item = monday_client.items.move_item_to_group(item_id=item_id, group_id=group_id)
    return [
        types.TextContent(
            type="text",
            text=f"Moved item {item_id} to group {group_id}. ID of the moved item: {item['data']['move_item_to_group']['id']}",
        )
    ]


async def handle_monday_delete_item(
    monday_client: MondayClient, item_id: str
) -> list[types.TextContent]:
    """
    Delete an item from a Monday.com board.

    Args:
        monday_client (MondayClient): The Monday.com client.
        item_id (str): The ID of the item to delete.
    """
    monday_client.items.delete_item_by_id(item_id=item_id)
    return [types.TextContent(type="text", text=f"Deleted item {item_id}.")]


async def handle_monday_archive_item(
    monday_client: MondayClient, item_id: str
) -> list[types.TextContent]:
    """
    Archive an item from a Monday.com board.

    Args:
        monday_client (MondayClient): The Monday.com client.
        item_id (str): The ID of the item to archive.
    """
    monday_client.items.archive_item_by_id(item_id=item_id)
    return [types.TextContent(type="text", text=f"Archived item {item_id}.")]
