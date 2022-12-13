import os
import re
from typing import Optional


def get_ansys_root(release_version: Optional[str] = None) -> str:
    """Identify the ansys executable based on the release version (e.g. "201")"""

    if release_version is None:
        awp_regex = re.compile("^AWP_ROOT([1-9]{3})$")
        available_versions = []
        for key in os.environ:
            match = re.match(awp_regex, key)
            if not match:
                continue
            available_versions.append(match.groups()[0])
        if not available_versions:
            raise RuntimeError(
                "No 'AWP_ROOT*' environment variable defined; the 'release_version' "
                "needs to be explicitly specified."
            )
        release_version = max(available_versions)

    awp_root_varname = f"AWP_ROOT{release_version}"

    if os.name == "nt":
        program_files = os.getenv("PROGRAMFILES", os.path.join("c:\\", "Program Files"))
        ans_root = os.getenv(
            awp_root_varname,
            os.path.join(program_files, "ANSYS Inc", f"v{release_version}"),
        )
        if not os.path.exists(ans_root):
            raise FileNotFoundError(f"Ansys installation directory {ans_root} does not exist.")
    else:
        if awp_root_varname in os.environ:
            ans_root = os.environ[awp_root_varname]
        else:
            candidate_root_dirs = [
                os.path.join("/", "usr", "ansys_inc", f"v{release_version}"),
                os.path.join("/", "ansys_inc", f"v{release_version}"),
            ]

            for candidate_dir in candidate_root_dirs:
                ans_root = candidate_dir
                if os.path.exists(ans_root):
                    break
            else:
                raise FileNotFoundError(
                    f"No Ansys installation found for version '{release_version}'.\n"
                    f"Tried: {candidate_root_dirs}."
                )

    return ans_root
