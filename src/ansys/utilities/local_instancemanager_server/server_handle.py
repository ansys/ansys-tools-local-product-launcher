from __future__ import annotations

from typing import Any
import weakref

import grpc

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

    def check(self) -> bool:
        return self._launcher.check()

    @property
    def url(self) -> str:
        return self._launcher.url

    @property
    def closed(self) -> bool:
        return not self._finalizer.alive


class GrpcServerHandle(ServerHandle):
    def __init__(self, *, launcher: LauncherProtocol[LAUNCHER_CONFIG_T]):
        super().__init__(launcher=launcher)
        self._channel = grpc.insecure_channel(self.url)

    @property
    def channel(self) -> grpc.Channel:
        return self._channel
