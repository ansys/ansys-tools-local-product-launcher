import importlib.metadata

# Can be replaced with import from importlib.metadata when Python 3.9 is no
# longer supported.
from backports.entry_points_selectable import entry_points

from .interface import LAUNCHER_CONFIG_T, LauncherProtocol

LAUNCHER_ENTRY_POINT = "ansys.tools.local_product_launcher.launcher"


def get_launcher(
    *, product_name: str, launch_mode: str
) -> type[LauncherProtocol[LAUNCHER_CONFIG_T]]:
    """Get the launcher plugin for a given product and launch mode."""
    ep_name = f"{product_name}.{launch_mode}"
    for entrypoint in _get_entry_points():
        if entrypoint.name == ep_name:
            return entrypoint.load()  # type: ignore
    else:
        raise KeyError(f"No plugin found for '{ep_name}'.")


def get_config_model(*, product_name: str, launch_mode: str) -> type[LAUNCHER_CONFIG_T]:
    """Get the configuration model for a given product and launch mode."""
    return get_launcher(product_name=product_name, launch_mode=launch_mode).CONFIG_MODEL


def get_all_plugins() -> dict[str, dict[str, LauncherProtocol[LAUNCHER_CONFIG_T]]]:
    """Get mapping {"<product_name>": {"<launch_mode>": Launcher}} containing all plugins."""
    res: dict[str, dict[str, LauncherProtocol[LAUNCHER_CONFIG_T]]] = dict()
    for entry_point in _get_entry_points():
        product_name, launch_mode = entry_point.name.split(".")
        res.setdefault(product_name, dict())
        res[product_name][launch_mode] = entry_point.load()
    return res


def _get_entry_points() -> tuple[importlib.metadata.EntryPoint, ...]:
    """Get all Local Product Launcher plugin entry points."""
    try:
        return entry_points(group=LAUNCHER_ENTRY_POINT)  # type: ignore
    except KeyError:
        return tuple()
