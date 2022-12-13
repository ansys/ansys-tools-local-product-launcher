from __future__ import annotations

from abc import ABC
import subprocess
from typing import TextIO

from ..interface import LAUNCHER_CONFIG_T, LauncherProtocol


class DirectLauncherBase(LauncherProtocol[LAUNCHER_CONFIG_T], ABC):
    def __init__(self) -> None:
        self._process: subprocess.Popen[str]
        self._stdout: TextIO
        self._stderr: TextIO

    def _start(self, *, process: subprocess.Popen[str], stdout: TextIO, stderr: TextIO) -> None:
        self._process = process
        self._stdout = stdout
        self._stderr = stderr

    def stop(self) -> None:
        self._process.terminate()
        self._process.wait()
        self._stdout.close()
        self._stderr.close()
