from typing import Tuple, Type

try:
    import importlib.metadata as importlib_metadata  # type: ignore
except ModuleNotFoundError:
    import importlib_metadata  # type: ignore

from .interface import LAUNCHER_CONFIG_T, LauncherProtocol

LAUNCHER_ENTRY_POINT = "local_pim_server.launcher"


def get_entry_points() -> Tuple[importlib_metadata.EntryPoint, ...]:
    try:
        return importlib_metadata.entry_points()[LAUNCHER_ENTRY_POINT]  # type: ignore
    except KeyError:
        return tuple()


def get_launcher(
    *, product_name: str, launch_method: str
) -> Type[LauncherProtocol[LAUNCHER_CONFIG_T]]:
    ep_name = f"{product_name}.{launch_method}"
    for entrypoint in get_entry_points():
        if entrypoint.name == ep_name:
            return entrypoint.load()  # type: ignore
    else:
        raise KeyError(f"No plugin found for '{ep_name}'.")
