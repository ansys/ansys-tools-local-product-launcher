# Copyright (C) 2024 ANSYS, Inc. and/or its affiliates.
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

"""Interface definitions for implementing a local product launcher.

A plugin for the Local Product Launcher must implement the :class:`LauncherProtocol`,
and register it
"""

from enum import Enum, auto
from typing import Any, ClassVar, Optional, Protocol, TypeVar

__all__ = [
    "LAUNCHER_CONFIG_T",
    "METADATA_KEY_DOC",
    "METADATA_KEY_NOPROMPT",
    "DataclassProtocol",
    "LauncherProtocol",
    "ServerType",
]

METADATA_KEY_DOC = "launcher_doc"
"""Key used in the :py:class:`dataclasses.Field` ``metadata``, for the option description."""

METADATA_KEY_NOPROMPT = "launcher_noprompt"
"""
Key used in the :py:class:`dataclasses.Field` ``metadata``, to skip prompting for
the option by default.
"""


class DataclassProtocol(Protocol):
    """Protocol class for Python dataclasses."""

    __dataclass_fields__: ClassVar[dict[str, Any]]


LAUNCHER_CONFIG_T = TypeVar("LAUNCHER_CONFIG_T", bound=DataclassProtocol)
# This docstring is commented-out because numpydoc causes the documentation build to fail when
# it is included.
# """Type variable for launcher configuration objects."""


class ServerType(Enum):
    """Defines which protocols the server supports.

    The ``ServerType`` is used as values in :attr:`LauncherProtocol.SERVER_SPEC`,
    to define the capabilities of the servers started with a given product and
    launch method.
    """

    GENERIC = auto()
    """Generic server, which responds at a given URL and port.

    The generic server type can be used for any server, and does not
    include information about which protocol should be used.
    """

    GRPC = auto()
    """Server which can be accessed via gRPC.

    Servers of this type are accessible via :attr:`.ProductInstance.channels`.
    """


class LauncherProtocol(Protocol[LAUNCHER_CONFIG_T]):
    """Interface for managing a local product instance.

    A plugin to the Local Product Launcher must implement the interface
    defined in this class.

    To check for compatibility, it is recommended to derive from this
    class, for example ``MyLauncher(LauncherProtocol[MyConfigModel])``, and
    check the resulting code with `mypy <https://mypy.readthedocs.io>`_.

    The ``__init__`` method should accept exactly one, keyword-only
    parameter ``config``. Note that this is `not enforced by mypy
    <https://bugs.python.org/issue44807>`_.

    Parameters
    ----------
    config :
        Configuration options used when starting the product. Must
        be an instance of ``CONFIG_MODEL``.
    """

    CONFIG_MODEL: type[LAUNCHER_CONFIG_T]
    """Defines the configuration options for the launcher.

    The configuration options which this launcher accepts, specified
    as a :py:func:`dataclass <dataclasses.dataclass>`. Note that the
    ``default`` and ``metadata[METADATA_KEY_DOC]`` of the fields are
    used in the configuration CLI, if available.
    """

    SERVER_SPEC: dict[str, ServerType]
    """Defines the server type(s) that are started.

    For example,

    .. code:: python

        SERVER_SPEC = {
            "MAIN": ServerType.GENERIC,
            "FILE_TRANSFER": ServerType.GRPC
        }

    defines a server which is accessible via URL at the ``"MAIN"`` key,
    and a server accessible via gRPC at the ``"FILE_TRANSFER"`` key.

    The :attr:`.ProductInstance.urls` then has keys ``{"MAIN", "FILE_TRANSFER"}``,
    whereas :meth:`.ProductInstance.channels` property only has the
    ``"FILE_TRANSFER"`` key.
    """

    def __init__(self, *, config: LAUNCHER_CONFIG_T):
        pass

    def start(self) -> None:
        """Start the product instance."""

    def stop(self, *, timeout: Optional[float] = None) -> None:
        """Tear down the product instance.

        Parameters
        ----------
        timeout :
            Time after which the instance can be forcefully stopped.
            The timeout should be interpreted as a hint to the implementation.
            It is not _required_ to trigger a force-shutdown, but the stop
            _must_ return within a finite time.
        """

    def check(self, *, timeout: Optional[float] = None) -> bool:
        """Check if the product instance is responding to requests.

        Parameters
        ----------
        timeout :
            Timeout in seconds for the check.
            The timeout should be interpreted as a hint to the implementation.
            It is not _required_ to return within the given time, but the
            check _must_ return within a finite time (i.e., it must not
            hang indefinitely).

        Returns
        -------
        :
            Whether the product instance is responding.
        """

    @property
    def urls(self) -> dict[str, str]:
        """Provide the URLs on which the server is listening.

        The keys of the returned dictionary must correspond to the ones
        defined in :attr:`.LauncherProtocol.SERVER_SPEC`.
        """
