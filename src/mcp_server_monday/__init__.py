import asyncio

from . import fastmcp_server


def main():
    """Main entry point for the package."""
    asyncio.run(fastmcp_server.run_server())


__all__ = ["main", "fastmcp_server"]