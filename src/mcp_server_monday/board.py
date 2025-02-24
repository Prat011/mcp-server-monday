import json

from mcp import types
from monday import MondayClient


def handle_monday_get_board_groups(
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
            text=f"Got the columns of a Monday.com board. {json.dumps(response)}",
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
