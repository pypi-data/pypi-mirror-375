"""wolflive - Python port of WOLFApi-TS (async-first, aiohttp + websockets)

This package provides an async-friendly client (WolfClient) that mirrors common
methods from the TypeScript library while offering a pythonic surface. A synchronous
adapter is provided for apps that prefer blocking APIs.
"""
from .client import WolfClient
from .sync_adapter import WolfClientSync

__all__ = ["WolfClient", "WolfClientSync"]
