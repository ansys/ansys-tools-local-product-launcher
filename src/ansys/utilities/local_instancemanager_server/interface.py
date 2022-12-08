"""Interface definitions for implementing a local product launcher."""

from enum import Enum, auto
from typing import Dict, Type, TypeVar

try:
    from typing import Protocol
except ImportError:
    from typing_extensions import Protocol  # type: ignore

import pydantic

__all__ = ["LAUNCHER_CONFIG_T", "LauncherProtocol"]

LAUNCHER_CONFIG_T = TypeVar("LAUNCHER_CONFIG_T", bound="pydantic.BaseModel")


class ServerType(Enum):
    GENERIC = auto()
    GRPC = auto()


class LauncherProtocol(Protocol[LAUNCHER_CONFIG_T]):
    """Manages a local product instance.

    It is recommended (but not required) to derive from this class,
    e.g. ``MyLauncher(LauncherProtocol[MyConfigModel]``, and check the
    resulting code with ``mypy``.
    Otherwise, compatibility with the interface will not be checked.
    """

    CONFIG_MODEL: Type[LAUNCHER_CONFIG_T]
    SERVER_SPEC: Dict[str, ServerType]

    def __init__(self, *, config: LAUNCHER_CONFIG_T):
        """Launch a local product instance with the given configuration."""

    def close(self) -> None:
        """Tear down the product instance."""

    def check(self) -> bool:
        """Check if the product instance is responding to requests."""

    @property
    def urls(self) -> Dict[str, str]:
        """Provide the URLs on which the server is listening."""
