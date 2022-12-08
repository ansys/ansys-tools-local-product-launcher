from __future__ import annotations

import time
from typing import Any, Dict, Optional
import weakref

import grpc

from .interface import LAUNCHER_CONFIG_T, LauncherProtocol, ServerType


class ServerHandle:
    def __init__(self, *, launcher: LauncherProtocol[LAUNCHER_CONFIG_T]):
        self._launcher = launcher
        self._finalizer: weakref.finalize
        self._urls: Dict[str, str]
        self._channels: Dict[str, grpc.Channel]
        self.start()

    def __enter__(self) -> ServerHandle:
        return self

    def __exit__(self, *exc: Any) -> None:
        self.stop()

    def start(self) -> None:
        if not self.stopped:
            raise RuntimeError("Cannot start the server, it has already been started.")
        self._finalizer = weakref.finalize(
            self,
            self._launcher.stop,
        )
        self._launcher.start()
        self._channels = dict()
        urls = self.urls
        if urls.keys() != self._launcher.SERVER_SPEC.keys():
            raise RuntimeError(
                f"The URL keys '{urls.keys()}' provided by the launcher "
                f"do not match the SERVER_SPEC keys '{self._launcher.SERVER_SPEC.keys()}'"
            )
        for key, server_type in self._launcher.SERVER_SPEC.items():
            if server_type == ServerType.GRPC:
                self._channels[key] = grpc.insecure_channel(urls[key])

    def stop(self) -> None:
        if self.stopped:
            raise RuntimeError("Cannot stop the server, it has already been stopped.")
        self._finalizer()

    def restart(self) -> None:
        self.stop()
        self.start()

    def check(self, timeout: Optional[float] = None) -> bool:
        return self._launcher.check(timeout=timeout)

    def wait(self, timeout: float) -> None:
        """Wait for all servers to respond.

        Repeatedly checks if the server(s) are running, returning as soon
        as they are all ready.

        Parameters
        ----------
        timeout :
            Wait time before raising an exception.

        Raises
        ------
        RuntimeError :
            In case the server still has not responded after ``timeout`` seconds.
        """
        start_time = time.time()
        while time.time() - start_time <= timeout:
            if self.check(timeout=timeout / 3):
                break
            else:
                # Try again until the timeout is reached. We add a small
                # delay s.t. the server isn't bombarded with requests.
                time.sleep(timeout / 100)
        else:
            raise RuntimeError(f"The product is not running after {timeout}s.")

    @property
    def urls(self) -> Dict[str, str]:
        return self._launcher.urls

    @property
    def stopped(self) -> bool:
        try:
            return not self._finalizer.alive
        # If the server has never been started, the '_finalizer' attribute
        # may not be defined.
        except AttributeError:
            return True

    @property
    def channels(self) -> Dict[str, grpc.Channel]:
        return self._channels
