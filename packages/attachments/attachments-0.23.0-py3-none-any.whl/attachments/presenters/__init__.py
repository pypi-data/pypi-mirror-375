"""Presenters package - formats attachment objects for output."""

# Import all presenter modules to register them
from . import data, metadata, text, visual

# Re-export commonly used functions if needed
__all__ = ["text", "visual", "data", "metadata"]
