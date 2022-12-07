from typing import Tuple

try:
    import importlib.metadata as importlib_metadata  # type: ignore
except ModuleNotFoundError:
    import importlib_metadata  # type: ignore

LAUNCHER_ENTRY_POINT = "local_pim_server.launcher"


def get_entry_points() -> Tuple[importlib_metadata.EntryPoint, ...]:
    try:
        return importlib_metadata.entry_points()[LAUNCHER_ENTRY_POINT]  # type: ignore
    except KeyError:
        return tuple()
