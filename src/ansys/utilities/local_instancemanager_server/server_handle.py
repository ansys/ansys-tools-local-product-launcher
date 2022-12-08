from __future__ import annotations

from typing import Any, Dict
import weakref

import grpc

from .interface import LAUNCHER_CONFIG_T, LauncherProtocol, ServerType


class ServerHandle:
    def __init__(self, *, launcher: LauncherProtocol[LAUNCHER_CONFIG_T]):
        self._launcher = launcher

        self._finalizer = weakref.finalize(
            self,
            self._launcher.close,
        )
        self._channels: Dict[str, grpc.Channel] = dict()
        urls = self.urls
        if urls.keys() != launcher.SERVER_SPEC.keys():
            raise RuntimeError(
                f"The URL keys '{urls.keys()}' provided by the launcher "
                f"do not match the SERVER_SPEC keys '{launcher.SERVER_SPEC.keys()}'"
            )
        for key, server_type in launcher.SERVER_SPEC.items():
            if server_type == ServerType.GRPC:
                self._channels[key] = grpc.insecure_channel(urls[key])

    def __enter__(self) -> ServerHandle:
        return self

    def __exit__(self, *exc: Any) -> None:
        self.close()

    def close(self) -> None:
        self._finalizer()

    def check(self) -> bool:
        return self._launcher.check()

    @property
    def urls(self) -> Dict[str, str]:
        return self._launcher.urls

    @property
    def closed(self) -> bool:
        return not self._finalizer.alive

    @property
    def channels(self) -> Dict[str, grpc.Channel]:
        return self._channels
