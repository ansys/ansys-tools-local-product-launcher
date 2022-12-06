"""
utilities.

local_instancemanager_server
"""

try:
    import importlib.metadata as importlib_metadata  # type: ignore
except ModuleNotFoundError:
    import importlib_metadata  # type: ignore

from . import interface

__version__ = importlib_metadata.version(__name__.replace(".", "-"))

__all__ = ["interface"]
