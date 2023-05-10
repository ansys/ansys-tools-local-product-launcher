"""
tools.

local_product_launcher
"""

import importlib.metadata

from . import config, helpers, interface, product_instance
from .launch import launch_product

__version__ = importlib.metadata.version(__name__.replace(".", "-"))

__all__ = [
    "interface",
    "helpers",
    "config",
    "product_instance",
    "launch_product",
]
