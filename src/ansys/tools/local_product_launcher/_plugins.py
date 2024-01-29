# Copyright (C) 2024 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import importlib.metadata

# Can be replaced with import from importlib.metadata when Python 3.9 is no
# longer supported.
from backports.entry_points_selectable import entry_points

from .interface import LAUNCHER_CONFIG_T, LauncherProtocol
from .product_instance import ProductInstance

LAUNCHER_ENTRY_POINT = "ansys.tools.local_product_launcher.launcher"
PRODUCT_INSTANCE_CLASS_ENTRY_POINT = "ansys.tools.local_product_launcher.product_instance_class"


def get_launcher(
    *, product_name: str, launch_mode: str
) -> type[LauncherProtocol[LAUNCHER_CONFIG_T]]:
    """Get the launcher plugin for a given product and launch mode."""
    ep_name = f"{product_name}.{launch_mode}"
    for entrypoint in _get_launcher_entry_points():
        if entrypoint.name == ep_name:
            return entrypoint.load()  # type: ignore
    else:
        raise KeyError(f"No plugin found for '{ep_name}'.")


def get_config_model(*, product_name: str, launch_mode: str) -> type[LAUNCHER_CONFIG_T]:
    """Get the configuration model for a given product and launch mode."""
    return get_launcher(product_name=product_name, launch_mode=launch_mode).CONFIG_MODEL


def get_all_launcher_plugins() -> dict[str, dict[str, LauncherProtocol[LAUNCHER_CONFIG_T]]]:
    """Get mapping {"<product_name>": {"<launch_mode>": Launcher}} containing all plugins."""
    res: dict[str, dict[str, LauncherProtocol[LAUNCHER_CONFIG_T]]] = dict()
    for entry_point in _get_launcher_entry_points():
        product_name, launch_mode = entry_point.name.split(".")
        res.setdefault(product_name, dict())
        res[product_name][launch_mode] = entry_point.load()
    return res


def _get_launcher_entry_points() -> tuple[importlib.metadata.EntryPoint, ...]:
    """Get all Local Product Launcher plugin entry points for launchers."""
    try:
        return entry_points(group=LAUNCHER_ENTRY_POINT)  # type: ignore
    except KeyError:
        return tuple()


def _get_product_instance_class_entry_points() -> tuple[importlib.metadata.EntryPoint, ...]:
    """Get all Local Product Launcher plugin entry points for plugin instance classes."""
    try:
        return entry_points(group=PRODUCT_INSTANCE_CLASS_ENTRY_POINT)  # type: ignore
    except KeyError:
        return tuple()


def get_product_instance_class(*, product_name: str, launch_mode: str) -> type[ProductInstance]:
    """Get the product instance class for a given product and launch mode."""
    res_cls = ProductInstance

    for entrypoint in _get_product_instance_class_entry_points():
        if entrypoint.name == f"{product_name}.{launch_mode}":
            return entrypoint.load()  # type: ignore
        elif entrypoint.name == product_name:
            res_cls = entrypoint.load()
    return res_cls
