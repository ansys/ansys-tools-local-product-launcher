"""Helpers for managing port assignment."""

from contextlib import ExitStack, closing
import socket


def find_free_ports(num_ports: int = 1) -> list[int]:
    """Find free ports on localhost.

    .. note::

        Since there is no way to reserve a port that would still allow
        a server to connect to it, there is no guarantee that the ports
        are *still* free when it is eventually used.

    Parameters
    ----------
    num_ports :
        The number of free ports to obtain.
    """
    port_list = []
    with ExitStack() as context_stack:
        for _ in range(num_ports):
            sock = context_stack.enter_context(closing(socket.socket()))
            sock.bind(("", 0))
            port_list.append(sock.getsockname()[1])
    return port_list
