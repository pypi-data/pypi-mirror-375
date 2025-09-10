"""Text presenters - markdown, plain text, CSV, XML output formats."""

from .markdown import *
from .plain import *
from .structured import *

__all__ = [
    # Markdown presenters
    "markdown",
    # Plain text presenters
    "text",
    # Structured text presenters
    "csv",
    "xml",
]
