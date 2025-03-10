import asyncio

from . import server
from . import document


def main():
    """Main entry point for the package."""
    asyncio.run(server.main())


__all__ = ["main", "server", "document"]
