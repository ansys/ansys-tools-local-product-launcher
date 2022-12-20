"""Interface definitions for implementing a local product launcher.

A plugin for the Local Product Launcher must implement the :class:`LauncherProtocol`,
and register it
"""

from enum import Enum, auto
from typing import Any, ClassVar, Dict, Optional, Type, TypeVar

try:
    from typing import Protocol
except ImportError:
    from typing_extensions import Protocol  # type: ignore

__all__ = [
    "LAUNCHER_CONFIG_T",
    "DOC_METADATA_KEY",
    "DataclassProtocol",
    "LauncherProtocol",
    "ServerType",
]

DOC_METADATA_KEY = "launcher_doc"
"""Key used in the :py:class:`dataclasses.Field` ``metadata``, for the option description."""


class DataclassProtocol(Protocol):
    """Protocol class for Python dataclasses."""

    __dataclass_fields__: ClassVar[Dict[str, Any]]


LAUNCHER_CONFIG_T = TypeVar("LAUNCHER_CONFIG_T", bound=DataclassProtocol)
"""Type variable for launcher configuration objects."""


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

    CONFIG_MODEL: Type[LAUNCHER_CONFIG_T]
    """Defines the configuration options for the launcher.

    The configuration options which this launcher accepts, specified
    as a :py:func:`dataclass <dataclasses.dataclass>`. Note that the
    ``default`` and ``metadata[DOC_METADATA_KEY]`` of the fields are
    used in the configuration CLI, if available.
    """

    SERVER_SPEC: Dict[str, ServerType]
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

    def stop(self) -> None:
        """Tear down the product instance."""

    def check(self, *, timeout: Optional[float] = None) -> bool:
        """Check if the product instance is responding to requests.

        Parameters
        ----------
        timeout :
            Timeout in seconds for the
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
    def urls(self) -> Dict[str, str]:
        """Provide the URLs on which the server is listening.

        The keys of the returned dictionary must correspond to the ones
        defined in :attr:`.LauncherProtocol.SERVER_SPEC`.
        """
