from __future__ import annotations

from typing import Any
import weakref

from .interface import LAUNCHER_CONFIG_T, LauncherProtocol


class ServerHandle:
    def __init__(self, *, launcher: LauncherProtocol[LAUNCHER_CONFIG_T]):
        self._launcher = launcher

        self._finalizer = weakref.finalize(
            self,
            self._launcher.close,
        )

    def __enter__(self) -> ServerHandle:
        return self

    def __exit__(self, *exc: Any) -> None:
        self.close()

    def close(self) -> None:
        self._finalizer()

    @property
    def url(self) -> str:
        return self._launcher.url

    @property
    def closed(self) -> bool:
        return not self._finalizer.alive
