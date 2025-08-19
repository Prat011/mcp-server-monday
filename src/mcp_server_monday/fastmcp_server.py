"""FastMCP-based Monday.com server implementation."""

import asyncio
import logging
import os
from typing import Any, Dict, List, Optional

from fastmcp import FastMCP
from monday import MondayClient

from mcp_server_monday.board import (
    handle_monday_create_board,
    handle_monday_create_new_board_group,
    handle_monday_get_board_columns,
    handle_monday_get_board_groups,
    handle_monday_list_boards,
)
from mcp_server_monday.constants import MONDAY_API_KEY
from mcp_server_monday.item import (
    handle_monday_archive_item,
    handle_monday_create_item,
    handle_monday_create_update_on_item,
    handle_monday_delete_item,
    handle_monday_get_item_by_id,
    handle_monday_get_item_updates,
    handle_monday_list_items_in_groups,
    handle_monday_list_subitems_in_items,
    handle_monday_move_item_to_group,
    handle_monday_update_item,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("fastmcp-server-monday")

mcp = FastMCP("monday")
monday_client: MondayClient = None


def get_monday_client() -> MondayClient:
    global monday_client
    if monday_client is None:
        monday_client = MondayClient(MONDAY_API_KEY)
    return monday_client


@mcp.tool()
async def monday_list_boards(limit: int = 100, page: int = 1) -> str:
    """Get all Boards from Monday.com.

    Args:
        limit: Maximum number of Monday.com Boards to return.
        page: Page number for pagination.
    """
    try:
        client = get_monday_client()
        result = await handle_monday_list_boards(client, limit, page)
        return result[0].text
    except Exception as e:
        return f"Error listing boards: {e}"


@mcp.tool()
async def monday_get_board_groups(boardId: str) -> str:
    """Get the Groups of a Monday.com Board.

    Args:
        boardId: Monday.com Board ID that the Item or Sub-item is on.
    """
    try:
        client = get_monday_client()
        result = await handle_monday_get_board_groups(boardId, client)
        return result[0].text
    except Exception as e:
        return f"Error getting board groups: {e}"


@mcp.tool()
async def monday_get_board_columns(boardId: str) -> str:
    """Get the Columns of a Monday.com Board.

    Args:
        boardId: Monday.com Board ID that the Item or Sub-item is on.
    """
    try:
        client = get_monday_client()
        result = await handle_monday_get_board_columns(boardId, client)
        return result[0].text
    except Exception as e:
        return f"Error getting board columns: {e}"


@mcp.tool()
async def monday_create_board(boardName: str, boardKind: Optional[str] = None) -> str:
    """Create a new Monday.com board.

    Args:
        boardName: Name of the Monday.com board to create.
        boardKind: Kind of the Monday.com board to create (public, private, shareable). Default is public.
    """
    try:
        client = get_monday_client()
        result = await handle_monday_create_board(
            boardName, boardKind or "public", client
        )
        return result[0].text
    except Exception as e:
        return f"Error creating board: {e}"


@mcp.tool()
async def monday_create_board_group(boardId: str, groupName: str) -> str:
    """Create a new group in a Monday.com board.

    Args:
        boardId: Monday.com Board ID that the group will be created in.
        groupName: Name of the group to create.
    """
    try:
        client = get_monday_client()
        result = await handle_monday_create_new_board_group(boardId, groupName, client)
        return result[0].text
    except Exception as e:
        return f"Error creating board group: {e}"


@mcp.tool()
async def monday_create_item(
    boardId: str,
    itemTitle: str,
    groupId: Optional[str] = None,
    parentItemId: Optional[str] = None,
    columnValues: Optional[Dict[str, Any]] = None,
) -> str:
    """Create a new item in a Monday.com Board. Optionally, specify the parent Item ID to create a Sub-item.

    Args:
        boardId: Monday.com Board ID that the Item or Sub-item is on.
        itemTitle: Name of the Monday.com Item or Sub-item that will be created.
        groupId: Monday.com Board's Group ID to create the Item in. If set, parentItemId should not be set.
        parentItemId: Monday.com Item ID to create the Sub-item under. If set, groupId should not be set.
        columnValues: Dictionary of column values to set {column_id: value}.
    """
    try:
        client = get_monday_client()
        result = await handle_monday_create_item(
            boardId, itemTitle, groupId, parentItemId, columnValues, client
        )
        return result[0].text
    except Exception as e:
        return f"Error creating item: {e}"


@mcp.tool()
async def monday_get_items_by_id(itemId: str) -> str:
    """Fetch specific Monday.com item by its ID.

    Args:
        itemId: ID of the Monday.com item to fetch.
    """
    try:
        client = get_monday_client()
        result = await handle_monday_get_item_by_id(itemId, client)
        return result[0].text
    except Exception as e:
        return f"Error fetching item: {e}"


@mcp.tool()
async def monday_update_item(
    boardId: str, itemId: str, columnValues: Dict[str, Any]
) -> str:
    """Update a Monday.com item's or sub-item's column values.

    Args:
        boardId: Monday.com Board ID that the Item or Sub-item is on.
        itemId: Monday.com Item or Sub-item ID to update the columns of.
        columnValues: Dictionary of column values to update the Monday.com Item or Sub-item with. ({column_id: value}).
    """
    try:
        client = get_monday_client()
        result = await handle_monday_update_item(boardId, itemId, columnValues, client)
        return result[0].text
    except Exception as e:
        return f"Error updating item: {e}"


@mcp.tool()
async def monday_create_update(itemId: str, updateText: str) -> str:
    """Create an update (comment) on a Monday.com Item or Sub-item.

    Args:
        itemId: Monday.com Item ID to create the update on.
        updateText: Content to update the Item or Sub-item with.
    """
    try:
        client = get_monday_client()
        result = await handle_monday_create_update_on_item(itemId, updateText, client)
        return result[0].text
    except Exception as e:
        return f"Error creating update: {e}"


@mcp.tool()
async def monday_list_items_in_groups(
    boardId: str, groupIds: List[str], limit: int, cursor: Optional[str] = None
) -> str:
    """List all items in the specified groups of a Monday.com board.

    Args:
        boardId: Monday.com Board ID that the Item or Sub-item is on.
        groupIds: List of group IDs to list items from.
        limit: Maximum number of items to return.
        cursor: Pagination cursor for continuing from previous results.
    """
    try:
        client = get_monday_client()
        result = await handle_monday_list_items_in_groups(
            boardId, groupIds, limit, cursor, client
        )
        return result[0].text
    except Exception as e:
        return f"Error listing items in groups: {e}"


@mcp.tool()
async def monday_list_subitems_in_items(itemIds: List[str]) -> str:
    """List all Sub-items of a list of Monday.com Items.

    Args:
        itemIds: List of Monday.com Item IDs to get sub-items for.
    """
    try:
        client = get_monday_client()
        result = await handle_monday_list_subitems_in_items(itemIds, client)
        return result[0].text
    except Exception as e:
        return f"Error listing sub-items: {e}"


@mcp.tool()
async def monday_move_item_to_group(itemId: str, groupId: str) -> str:
    """Move an item to a group in a Monday.com board.

    Args:
        itemId: Monday.com Item ID to move.
        groupId: Monday.com Group ID to move the Item to.
    """
    try:
        client = get_monday_client()
        result = await handle_monday_move_item_to_group(client, itemId, groupId)
        return result[0].text
    except Exception as e:
        return f"Error moving item: {e}"


@mcp.tool()
async def monday_delete_item(itemId: str) -> str:
    """Delete an item from a Monday.com board.

    Args:
        itemId: Monday.com Item ID to delete.
    """
    try:
        client = get_monday_client()
        result = await handle_monday_delete_item(client, itemId)
        return result[0].text
    except Exception as e:
        return f"Error deleting item: {e}"


@mcp.tool()
async def monday_archive_item(itemId: str) -> str:
    """Archive an item from a Monday.com board.

    Args:
        itemId: Monday.com Item ID to archive.
    """
    try:
        client = get_monday_client()
        result = await handle_monday_archive_item(client, itemId)
        return result[0].text
    except Exception as e:
        return f"Error archiving item: {e}"


@mcp.tool()
async def monday_get_item_updates(itemId: str, limit: int = 25) -> str:
    """Get updates for a specific item in Monday.com.

    Args:
        itemId: ID of the Monday.com item to get updates for.
        limit: Maximum number of updates to retrieve. Default is 25.
    """
    try:
        client = get_monday_client()
        result = await handle_monday_get_item_updates(itemId, limit, client)
        return result[0].text
    except Exception as e:
        return f"Error getting item updates: {e}"


def main():
    """Entry point for the FastMCP server."""
    asyncio.run(run_server())


async def run_server():
    """Run the FastMCP server with HTTP streaming transport."""
    # Configuration from environment variables
    host = os.getenv("FASTMCP_HOST", "0.0.0.0")
    port = int(os.getenv("FASTMCP_PORT", "8000"))
    path = os.getenv("FASTMCP_PATH", "/api/mcp/")

    logger.info("Starting Monday.com FastMCP server with HTTP streaming transport")
    logger.info(f"Server will be available at http://{host}:{port}{path}")

    global monday_client
    monday_client = MondayClient(MONDAY_API_KEY)
    await mcp.run_async(transport="http", host=host, port=port, path=path)


if __name__ == "__main__":
    main()
