"""
tools.

local_product_launcher
"""

try:
    import importlib.metadata as importlib_metadata  # type: ignore
except ModuleNotFoundError:
    import importlib_metadata  # type: ignore

from . import helpers, interface, plugins

__version__ = importlib_metadata.version(__name__.replace(".", "-"))

__all__ = [
    "interface",
    "helpers",
    "plugins",
]
