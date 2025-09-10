"""Loaders package - transforms files into attachment objects."""

# Import all loader modules to register them
from . import data, documents, media, repositories, web

# Re-export commonly used functions if needed
__all__ = ["documents", "media", "data", "web", "repositories"]
