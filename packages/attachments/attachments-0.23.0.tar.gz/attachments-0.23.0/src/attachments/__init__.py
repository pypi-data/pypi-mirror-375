"""Attachments - the Python funnel for LLM context

Turn any file into model-ready text + images, in one line."""

from . import adapt as _adapt_module

# Import config
# Import all loaders and presenters to register them
# Import pipelines to register processors
from . import config, loaders, pipelines, presenters
from . import modify as _modify_module

# Import other modules to register their functions
from . import refine as _refine_module
from . import split as _split_module
from .config import set_verbose
from .core import (
    A,
    Attachment,
    AttachmentCollection,
    Pipeline,
    SmartVerbNamespace,
    _adapters,
    _loaders,
    _modifiers,
    _presenters,
    _refiners,
    _splitters,
    adapter,
    attach,
    loader,
    modifier,
    presenter,
    refiner,
    splitter,
)

# Import DSL introspection tool
from .dsl_info import get_dsl_info
from .highest_level_api import Attachments, auto_attach
from .highest_level_api import process as simple
from .pipelines import processors

# Create the namespace instances after functions are registered
load = SmartVerbNamespace(_loaders, "load")
modify = SmartVerbNamespace(_modifiers, "modify")
present = SmartVerbNamespace(_presenters, "present")
adapt = SmartVerbNamespace(_adapters, "adapt")
refine = SmartVerbNamespace(_refiners, "refine")
split = SmartVerbNamespace(_splitters, "split")


# Dynamic version reading from pyproject.toml
def _get_version():
    """Read version from pyproject.toml"""
    import os
    from pathlib import Path

    # Try to find pyproject.toml starting from this file's directory
    current_dir = Path(__file__).parent
    for _ in range(3):  # Look up to 3 levels up
        pyproject_path = current_dir / "pyproject.toml"
        if pyproject_path.exists():
            try:
                content = pyproject_path.read_text(encoding="utf-8")
                for line in content.split("\n"):
                    if line.strip().startswith("version = "):
                        # Extract version from line like: version = "0.6.0"
                        version_part = line.split("=", 1)[1].strip()
                        # Remove any comments (# and everything after)
                        if "#" in version_part:
                            version_part = version_part.split("#", 1)[0].strip()
                        # Remove quotes
                        version = version_part.strip('"').strip("'")
                        return version
            except Exception:
                pass
        current_dir = current_dir.parent

    # Fallback: try importlib.metadata if package is installed
    try:
        from importlib.metadata import version

        return version("attachments")
    except ImportError:
        try:
            from importlib_metadata import version

            return version("attachments")
        except ImportError:
            pass

    return "unknown"


__version__ = _get_version()

__all__ = [
    # Core classes and functions
    "Attachment",
    "AttachmentCollection",
    "attach",
    "A",
    "Pipeline",
    # Config
    "config",
    "set_verbose",
    # DSL Introspection
    "get_dsl_info",
    # High-level API
    "Attachments",
    "simple",
    "auto_attach",
    # Namespace objects
    "load",
    "modify",
    "present",
    "adapt",
    "refine",
    "split",
    # Processors
    "processors",
    # Decorator functions
    "loader",
    "modifier",
    "presenter",
    "adapter",
    "refiner",
    "splitter",
    # Module imports
    "loaders",
    "presenters",
    "pipelines",
]
