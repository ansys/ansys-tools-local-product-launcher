from contextlib import ExitStack, closing
import socket
from typing import List


def find_free_ports(num_ports: int = 1) -> List[int]:
    """Find a free port on localhost.

    .. note::

        There is no guarantee that the port is *still* free when it is
        used by the calling code.
    """
    port_list = []
    with ExitStack() as context_stack:
        for _ in range(num_ports):
            sock = context_stack.enter_context(closing(socket.socket()))
            sock.bind(("", 0))
            port_list.append(sock.getsockname()[1])
    return port_list