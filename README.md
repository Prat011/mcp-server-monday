# Monday.com MCP server

[![smithery badge](https://smithery.ai/badge/@sakce/mcp-server-monday)](https://smithery.ai/server/@sakce/mcp-server-monday)

MCP Server for monday.com, enabling MCP clients to interact with Monday.com boards, items, updates, and documents.

<a href="https://glama.ai/mcp/servers/vobfpuod5x">
  <img width="380" height="200" src="https://glama.ai/mcp/servers/vobfpuod5x/badge" alt="Monday.com Server MCP server" />
</a>

## Components

### Tools

The server implements the following tools:

- `monday-create-item`: Creates a new item or sub-item in a Monday.com board
- `monday-get-board-groups`: Retrieves all groups from a specified Monday.com board
- `monday-create-update`: Creates a comment/update on a Monday.com item
- `monday-list-boards`: Lists all available Monday.com boards
- `monday-list-items-in-groups`: Lists all items in specified groups of a Monday.com board
- `monday-list-subitems-in-items`: Lists all sub-items for given Monday.com items
- `monday-create-board`: Creates a new Monday.com board
- `monday-create-board-group`: Creates a new group in a Monday.com board
- `monday-move-item-to-group`: Moves a Monday.com item to a different group
- `monday-delete-item`: Deletes a Monday.com item
- `monday-archive-item`: Archives a Monday.com item
- `monday-get-item-updates`: Retrieves updates/comments for a specific item
- `monday-get-docs`: Lists documents in Monday.com, optionally filtered by folder
- `monday-get-doc-content`: Retrieves the content of a specific document
- `monday-create-doc`: Creates a new document in Monday.com
- `monday-add-doc-block`: Adds a block to an existing document


## Setup

1. Create and save a personal API Token in Monday.com by following the instructions [here](https://developer.monday.com/api-reference/docs/authentication#developer-tab).
2. Get the Workspace Name from the URL of your Monday.com workspace. For example, if the URL is `https://myworkspace.monday.com/`, the workspace name is `myworkspace`.


## Quickstart

### Install


#### Claude Desktop

On MacOS: `~/Library/Application\ Support/Claude/claude_desktop_config.json`

On Windows: `%APPDATA%/Claude/claude_desktop_config.json`

##### Using uvx
  ```
  "mcpServers": {
    "monday": {
      "command": "uvx",
      "args": [
        "mcp-server-monday"
      ],
      "env": {
        "MONDAY_API_KEY": "your-monday-api-key",
        "MONDAY_WORKSPACE_NAME": "your-monday-workspace-name"
      }
    }
  }
  ```

##### Using Docker
  ```
  "mcpServers": {
    "monday-docker": {
      "command": "docker",
      "args": [
        "run", 
        "--rm", 
        "-i", 
        "-e",
        "MONDAY_API_KEY=your-monday-api-key",
        "-e",
        "MONDAY_WORKSPACE_NAME=your-monday-workspace-name",
        "sakce/mcp-server-monday"
      ]
    }
  }
  ```

#### Using Smithery

To install Monday.com MCP Server for Claude Desktop automatically via [Smithery](https://smithery.ai/server/@sakce/mcp-server-monday):

```bash
npx -y @smithery/cli install @sakce/mcp-server-monday --client claude
```

## Development

### Building and Publishing

To prepare the package for distribution:

1. Sync dependencies and update lockfile:
```bash
uv sync
```

2. Build package distributions:
```bash
uv build
```

This will create source and wheel distributions in the `dist/` directory.

3. Publish to PyPI:
```bash
uv publish
```

Note: You'll need to set PyPI credentials via environment variables or command flags:
- Token: `--token` or `UV_PUBLISH_TOKEN`
- Or username/password: `--username`/`UV_PUBLISH_USERNAME` and `--password`/`UV_PUBLISH_PASSWORD`

### Debugging

Since MCP servers run over stdio, debugging can be challenging. For the best debugging
experience, we strongly recommend using the [MCP Inspector](https://github.com/modelcontextprotocol/inspector).

You can launch the MCP Inspector via [`npm`](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm) with this command:

```bash
npx @modelcontextprotocol/inspector uv run mcp-server-monday
```

Upon launching, the Inspector will display a URL that you can access in your browser to begin debugging.