"""Interface definitions for implementing a local product launcher."""

try:
    from typing import Protocol
except ImportError:
    from typing_extensions import Protocol  # type: ignore

import pydantic


class LauncherProtocol(Protocol):
    """Manages a local product instance."""

    def __init__(self, config: pydantic.BaseModel):
        """Launch a local product instance with the given configuration."""

    def close(self) -> None:
        """Tear down the product instance."""

    def check(self) -> bool:
        """Check if the product instance is responding to requests."""
