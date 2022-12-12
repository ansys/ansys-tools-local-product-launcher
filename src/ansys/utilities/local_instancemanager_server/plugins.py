from typing import Dict, Tuple, Type

try:
    import importlib.metadata as importlib_metadata  # type: ignore
except ModuleNotFoundError:
    import importlib_metadata  # type: ignore

from .interface import LAUNCHER_CONFIG_T, LauncherProtocol

LAUNCHER_ENTRY_POINT = "local_pim_server.launcher"


def get_launcher(
    *, product_name: str, launch_mode: str
) -> Type[LauncherProtocol[LAUNCHER_CONFIG_T]]:
    ep_name = f"{product_name}.{launch_mode}"
    for entrypoint in _get_entry_points():
        if entrypoint.name == ep_name:
            return entrypoint.load()  # type: ignore
    else:
        raise KeyError(f"No plugin found for '{ep_name}'.")


def get_config_model(*, product_name: str, launch_mode: str) -> Type[LAUNCHER_CONFIG_T]:
    return get_launcher(product_name=product_name, launch_mode=launch_mode).CONFIG_MODEL


def get_all_plugins() -> Dict[str, Dict[str, LauncherProtocol[LAUNCHER_CONFIG_T]]]:
    res: Dict[str, Dict[str, LauncherProtocol[LAUNCHER_CONFIG_T]]] = dict()
    for entry_point in _get_entry_points():
        product_name, launch_mode = entry_point.name.split(".")
        res.setdefault(product_name, dict())
        res[product_name][launch_mode] = entry_point.load()
    return res


def _get_entry_points() -> Tuple[importlib_metadata.EntryPoint, ...]:
    try:
        return importlib_metadata.entry_points()[LAUNCHER_ENTRY_POINT]  # type: ignore
    except KeyError:
        return tuple()
