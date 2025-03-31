default:
  just --list

PACKAGE_NAME := "mcp-server-monday"

sync:
  uv sync

release version:
  sed -i '' "s/version = \".*\"/version = \"{{version}}\"/" pyproject.toml
  uv sync
  uv build
  git add pyproject.toml
  git commit -m "chore: bump version to {{version}}"
  git tag -a v{{version}} -m "Release version {{version}}"
  git push origin main v{{version}}
  uv publish dist/mcp_server_monday-{{version}}*

inspect-local-server:
	npx @modelcontextprotocol/inspector uv --directory . run {{PACKAGE_NAME}}
