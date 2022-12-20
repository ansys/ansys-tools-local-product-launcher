import dataclasses
import pathlib
import subprocess
import sys
from typing import Optional

import grpc

from ansys.tools.local_product_launcher.helpers.grpc import check_grpc_health
from ansys.tools.local_product_launcher.helpers.ports import find_free_ports
from ansys.tools.local_product_launcher.interface import (
    DOC_METADATA_KEY,
    LauncherProtocol,
    ServerType,
)

SCRIPT_PATH = pathlib.Path(__file__).parent / "simple_test_server.py"
SERVER_KEY = "main"


@dataclasses.dataclass
class SimpleLauncherConfig:
    script_path: str = dataclasses.field(
        default=str(SCRIPT_PATH),
        metadata={DOC_METADATA_KEY: "Location of the server Python script."},
    )


class SimpleLauncher(LauncherProtocol[SimpleLauncherConfig]):
    CONFIG_MODEL = SimpleLauncherConfig
    SERVER_SPEC = {SERVER_KEY: ServerType.GRPC}

    def __init__(self, *, config: SimpleLauncherConfig):
        self._script_path = config.script_path
        self._process: subprocess.Popen[str]
        self._url: str

    def start(self):
        port = find_free_ports()[0]
        self._url = f"localhost:{port}"
        self._process = subprocess.Popen(
            [
                sys.executable,
                self._script_path,
                str(port),
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            text=True,
        )

    def stop(self):
        self._process.kill()  # to speed up tests, directly use 'SIGKILL'
        self._process.wait()

    def check(self, *, timeout: Optional[float] = None) -> bool:
        channel = grpc.insecure_channel(self.urls[SERVER_KEY])
        return check_grpc_health(channel, timeout=timeout)

    @property
    def urls(self):
        return {SERVER_KEY: self._url}
