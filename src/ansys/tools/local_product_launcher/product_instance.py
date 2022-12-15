"""Defines a wrapper for interacting with launched product instances."""

from __future__ import annotations

import time
from typing import Any, Dict, Optional
import weakref

import grpc

from .interface import LAUNCHER_CONFIG_T, LauncherProtocol, ServerType

__all__ = ["ProductInstance"]


class ProductInstance:
    """Wrapper to interact with the launched product instance.

    Allows stopping / starting the product instance, and provides access
    to its server URLs / channels.

    The :class:`ProductInstance` can be used as a context manager, stopping
    the instance when exiting the context.
    """

    def __init__(self, *, launcher: LauncherProtocol[LAUNCHER_CONFIG_T]):
        self._launcher = launcher
        self._finalizer: weakref.finalize
        self._urls: Dict[str, str]
        self._channels: Dict[str, grpc.Channel]
        self.start()

    def __enter__(self) -> ProductInstance:
        """Enter the context manager defined by the product instance."""
        if self.stopped:
            raise RuntimeError("The product instance is stopped, cannot enter context.")
        return self

    def __exit__(self, *exc: Any) -> None:
        """Stop the product instance when exiting a context manager."""
        self.stop()

    def start(self) -> None:
        """Start the product instance.

        Raises
        ------
        RuntimeError
            If the instance is already in the started state.
        RuntimeError
            If the URLs exposed by the started instance do not match
            the expected ones defined in the launcher's
            :attr:`.LauncherProtocol.SERVER_SPEC`.
        """
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
        """Stop the product instance.

        Raises
        ------
        RuntimeError
            If the instance is already in the stopped state.
        """
        if self.stopped:
            raise RuntimeError("Cannot stop the server, it has already been stopped.")
        self._finalizer()

    def restart(self) -> None:
        """Stop, then start the product instance.

        Raises
        ------
        RuntimeError
            If the instance is already in the stopped state.
        RuntimeError
            If the URLs exposed by the started instance do not match
            the expected ones defined in the launcher's
            :attr:`.LauncherProtocol.SERVER_SPEC`.
        """
        self.stop()
        self.start()

    def check(self, timeout: Optional[float] = None) -> bool:
        """Check if all servers are responding to requests.

        Parameters
        ----------
        timeout :
            Time to wait for the servers to respond, in seconds. Note that
            there is guarantee that ``check`` will return within this time.
            This parameter is used as a hint to the launcher implementation.
        """
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
        RuntimeError
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
        """URL+port for the servers of the product instance."""
        return self._launcher.urls

    @property
    def stopped(self) -> bool:
        """Specify whether the product instance is currently stopped."""
        try:
            return not self._finalizer.alive
        # If the server has never been started, the '_finalizer' attribute
        # may not be defined.
        except AttributeError:
            return True

    @property
    def channels(self) -> Dict[str, grpc.Channel]:
        """Channels to the gRPC servers of the product instance."""
        return self._channels
