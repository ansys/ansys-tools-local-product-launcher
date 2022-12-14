"""
tools.

local_product_launcher
"""

try:
    import importlib.metadata as importlib_metadata  # type: ignore
except ModuleNotFoundError:
    import importlib_metadata  # type: ignore

from . import config, helpers, interface, product_instance
from .launch import launch_product

__version__ = importlib_metadata.version(__name__.replace(".", "-"))

__all__ = [
    "interface",
    "helpers",
    "config",
    "product_instance",
    "launch_product",
]
