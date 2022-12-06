"""Interface definitions for implementing a local product launcher."""

from typing import Type, TypeVar

try:
    from typing import Protocol
except ImportError:
    from typing_extensions import Protocol  # type: ignore

import pydantic

__all__ = ["LAUNCHER_CONFIG_T", "LauncherProtocol"]

LAUNCHER_CONFIG_T = TypeVar("LAUNCHER_CONFIG_T", bound="pydantic.BaseModel")


class LauncherProtocol(Protocol[LAUNCHER_CONFIG_T]):
    """Manages a local product instance."""

    CONFIG_MODEL: Type[LAUNCHER_CONFIG_T]

    def __init__(self, *, config: LAUNCHER_CONFIG_T):
        """Launch a local product instance with the given configuration."""

    def close(self) -> None:
        """Tear down the product instance."""

    def check(self) -> bool:
        """Check if the product instance is responding to requests."""


# TODO: Remove code below here; this is just to demonstrate / test how the
# protocol works. Mypy will check that the 'MyLauncher' matches the protocol.


class Foo(pydantic.BaseModel):
    x: int


class MyLauncher:
    CONFIG_MODEL = Foo

    def __init__(self, *, config: Foo):
        ...

    def close(self) -> None:
        ...

    def check(self) -> bool:
        ...


def foo(x: LauncherProtocol[LAUNCHER_CONFIG_T]) -> None:
    return


foo(MyLauncher(config=Foo(x=1)))
