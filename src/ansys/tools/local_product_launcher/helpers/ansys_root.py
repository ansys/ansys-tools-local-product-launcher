"""Helper to find the Ansys install directory."""

import os
import re
from typing import Optional


def get_ansys_root(release_version: Optional[str] = None) -> str:
    """Find the root of the Ansys install directory.

    Returns the root path of the Ansys installation for the specified
    version.

    Parameters
    ----------
    release_version :
        The release short-code (for example ``"231"``) for which the Ansys
        install directory should be found. If not specified, use the
        latest installed version.
    """
    if release_version is None:
        release_version = _get_release_version_from_envvar()

    ans_root = _get_ans_root_from_envvar(release_version)

    if ans_root is None:
        ans_root = _get_ans_root_from_default_locations(release_version)

    if not os.path.exists(ans_root):
        raise FileNotFoundError(f"Ansys installation directory {ans_root} does not exist.")
    return ans_root


def _get_release_version_from_envvar() -> Optional[str]:
    awp_regex = re.compile("^AWP_ROOT([1-9]{3})$")
    available_versions = []
    for key in os.environ:
        match = re.match(awp_regex, key)
        if not match:
            continue
        available_versions.append(match.groups()[0])
    if not available_versions:
        return None
    return max(available_versions)


def _get_ans_root_from_envvar(release_version: Optional[str]) -> Optional[str]:
    if release_version is None:
        return None
    awp_root_varname = f"AWP_ROOT{release_version}"
    return os.environ.get(awp_root_varname)


def _get_ans_root_from_default_locations(release_version: Optional[str]) -> str:
    if os.name == "nt":
        default_locations = [os.path.join("c:\\", "Program Files", "ANSYS Inc")]
    else:
        default_locations = [
            os.path.join("/", "usr", "ansys_inc"),
            os.path.join("/", "ansys_inc", f"v{release_version}"),
        ]

    if release_version is None:
        version_dir_regex = re.compile("^v([1-9]{3})$")
        available_versions = []
        for base_location in default_locations:
            for entry in os.listdir(base_location):
                match = re.match(version_dir_regex, entry)
                if not match:
                    continue
                available_versions.append(match.groups()[0])
        if not available_versions:
            raise FileNotFoundError(
                f"No Ansys install found in default locations {default_locations}."
            )
        release_version = max(available_versions)

    for base_location in default_locations:
        candidate_dir = os.path.join(base_location, f"v{release_version}")
        if os.path.exists(candidate_dir):
            return candidate_dir
    raise FileNotFoundError(
        f"No Ansys install for version '{release_version}' "
        f"found in default locations {default_locations}"
    )
