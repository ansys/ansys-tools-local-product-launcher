# Copyright (C) 2022 - 2024 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Defines a wrapper for interacting with launched product instances."""

from __future__ import annotations

import time
from typing import Any
import weakref

import grpc

from .interface import LAUNCHER_CONFIG_T, LauncherProtocol, ServerType

__all__ = ["ProductInstance"]

_GRPC_MAX_MESSAGE_LENGTH = 256 * 1024**2  # 256 MB


class ProductInstance:
    """Provides a wrapper for interacting with the launched product instance.

    This class allows stopping and starting of the product instance. It also
    provides access to its server URLs/channels.

    The :class:`ProductInstance` class can be used as a context manager, stopping
    the instance when exiting the context.
    """

    def __init__(self, *, launcher: LauncherProtocol[LAUNCHER_CONFIG_T]):
        self._launcher = launcher
        self._finalizer: weakref.finalize
        self._urls: dict[str, str]
        self._channels: dict[str, grpc.Channel]
        self.start()

    def __enter__(self) -> ProductInstance:
        """Enter the context manager defined by the product instance."""
        if self.stopped:
            raise RuntimeError("The product instance is stopped. Cannot enter context.")
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
            :attr:`.LauncherProtocol.SERVER_SPEC` attribute.
        """
        if not self.stopped:
            raise RuntimeError("Cannot start the server. It has already been started.")
        self._finalizer = weakref.finalize(self, self._launcher.stop, timeout=None)
        self._launcher.start()
        self._channels = dict()
        urls = self.urls
        if urls.keys() != self._launcher.SERVER_SPEC.keys():
            raise RuntimeError(
                f"The URL keys '{urls.keys()}' provided by the launcher "
                f"do not match the SERVER_SPEC keys '{self._launcher.SERVER_SPEC.keys()}'."
            )
        for key, server_type in self._launcher.SERVER_SPEC.items():
            if server_type == ServerType.GRPC:
                self._channels[key] = grpc.insecure_channel(
                    urls[key],
                    options=[("grpc.max_receive_message_length", _GRPC_MAX_MESSAGE_LENGTH)],
                )

    def stop(self, *, timeout: float | None = None) -> None:
        """Stop the product instance.

        Parameters
        ----------
        timeout :
            Time in seconds after which the instance is forcefully stopped.
            Not all launch methods implement this parameter. If the parameter
            is not implemented, it is ignored.

        Raises
        ------
        RuntimeError
            If the instance is already in the stopped state.
        """
        if self.stopped:
            raise RuntimeError("Cannot stop the server. It has already been stopped.")
        self._launcher.stop(timeout=timeout)
        self._finalizer.detach()

    def restart(self, stop_timeout: float | None = None) -> None:
        """Stop and then start the product instance.

        Parameters
        ----------
        stop_timeout :
            Time in seconds after which the instance is forcefully stopped.
            Not all launch methods implement this parameter. If the parameter
            is not implemented, it is ignored.

        Raises
        ------
        RuntimeError
            If the instance is already in the stopped state.
        RuntimeError
            If the URLs exposed by the started instance do not match
            the expected ones defined in the launcher's
            :attr:`.LauncherProtocol.SERVER_SPEC` attribute.
        """
        self.stop(timeout=stop_timeout)
        self.start()

    def check(self, timeout: float | None = None) -> bool:
        """Check if all servers are responding to requests.

        Parameters
        ----------
        timeout :
            Time in seconds to wait for the servers to respond. There
            is no guarantee that the ``check()`` method returns within this time.
            Instead, this parameter is used as a hint to the launcher implementation.
        """
        return self._launcher.check(timeout=timeout)

    def wait(self, timeout: float) -> None:
        """Wait for all servers to respond.

        This method repeatedly checks if the servers are running, returning as soon
        as they are all ready.

        Parameters
        ----------
        timeout :
            Wait time in seconds before raising an exception.

        Raises
        ------
        RuntimeError
            If the server still has not responded after ``timeout`` seconds.
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
    def urls(self) -> dict[str, str]:
        """URL and port for the servers of the product instance."""
        return self._launcher.urls

    @property
    def stopped(self) -> bool:
        """Flag indicating if the product instance is currently stopped."""
        try:
            return not self._finalizer.alive
        # If the server has never been started, the '_finalizer' attribute
        # may not be defined.
        except AttributeError:
            return True

    @property
    def channels(self) -> dict[str, grpc.Channel]:
        """Channels to the gRPC servers of the product instance."""
        return self._channels
