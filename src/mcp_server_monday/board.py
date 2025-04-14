import json

from mcp import types
from monday import MondayClient
from monday.resources.types import BoardKind


async def handle_monday_get_board_groups(
    boardId: str, monday_client: MondayClient
) -> list[types.TextContent]:
    """Get the Groups of a Monday.com Board."""
    response = monday_client.groups.get_groups_by_board(board_ids=boardId)
    return [
        types.TextContent(
            type="text",
            text=f"Got the groups of a Monday.com board. {json.dumps(response['data'])}",
        )
    ]


async def handle_monday_get_board_columns(
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
                    settings_str
                }}
            }}
        }}
    """
    response = monday_client.custom._query(query)
    for board in response.get("data", {}).get("boards", []):
        for column in board["columns"]:
            settings_str = column.pop("settings_str", None)
            if settings_str:
                if isinstance(settings_str, str):
                    try:
                        settings_obj = json.loads(settings_str)
                        if settings_obj.get("labels"):
                            column["available_labels"] = settings_obj["labels"]
                    except json.JSONDecodeError:
                        pass

    return [
        types.TextContent(
            type="text",
            text=f"Got the columns of a Monday.com board:\n{json.dumps(response)}",
        )
    ]


async def handle_monday_list_boards(
    monday_client: MondayClient, limit: int, page: int
) -> list[types.TextContent]:
    """List all available Monday.com boards"""
    response = monday_client.boards.fetch_boards(limit=limit, page=page)
    boards = response["data"]["boards"]

    board_list = "\n".join(
        [f"- {board['name']} (ID: {board['id']})" for board in boards]
    )

    return [
        types.TextContent(
            type="text", text=f"Available Monday.com Boards:\n{board_list}"
        )
    ]


async def handle_monday_create_board(
    monday_client: MondayClient, board_name: str, board_kind: str = "public"
) -> list[types.TextContent]:
    """
    Create a new Monday.com board.

    Args:
        monday_client (MondayClient): The Monday.com client.
        board_name (str): The name of the board.
        board_kind (str): The kind of board to create. Must be one of "public" or "private". Defaults to "public".
    """
    actual_board_kind = BoardKind(board_kind)
    board = monday_client.boards.create_board(
        board_name=board_name, board_kind=actual_board_kind
    )
    return [
        types.TextContent(
            type="text",
            text=f"Created monday board {board_name} of kind {board_kind}. ID of the new board: {board['data']['create_board']['id']}",
        )
    ]


async def handle_monday_create_new_board_group(
    monday_client: MondayClient, board_id: str, group_name: str
) -> list[types.TextContent]:
    """
    Create a new group in a Monday.com board.

    Args:
        monday_client (MondayClient): The Monday.com client.
        board_id (str): The ID of the board.
        group_name (str): The name of the group.
    """
    group = monday_client.groups.create_group(board_id=board_id, group_name=group_name)
    return [
        types.TextContent(
            type="text",
            text=f"Created new group {group_name} in board {board_id}. ID of the new group: {group['data']['create_group']['id']}",
        )
    ]
