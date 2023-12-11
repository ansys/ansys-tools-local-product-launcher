from dataclasses import dataclass

from ansys.tools.local_product_launcher import interface


@dataclass
class LauncherConfig:
    pass


class Launcher(interface.LauncherProtocol[LauncherConfig]):
    CONFIG_MODEL = LauncherConfig
