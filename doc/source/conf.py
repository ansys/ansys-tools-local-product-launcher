"""Sphinx documentation configuration file."""

from datetime import datetime
import os

from ansys_sphinx_theme import ansys_favicon, get_version_match

from ansys.tools.local_product_launcher import __version__

# Project information
project = "ansys-tools-local-product-launcher"
copyright = f"(c) {datetime.now().year} ANSYS, Inc. All rights reserved"
author = "ANSYS, Inc."
release = version = __version__

# Select desired logo, theme, and declare the html title
html_favicon = ansys_favicon
html_theme = "ansys_sphinx_theme"
html_short_title = html_title = "ansys-tools-local-product-launcher"

# specify the location of your github repo
cname = os.environ.get("DOCUMENTATION_CNAME", "local-product-launcher.tools.docs.pyansys.com")
"""The canonical name of the webpage hosting the documentation."""
html_theme_options = {
    "logo": "pyansys",
    "github_url": "https://github.com/ansys/ansys-tools-local-product-launcher",
    "show_prev_next": True,
    "show_breadcrumbs": True,
    "additional_breadcrumbs": [
        ("PyAnsys", "https://docs.pyansys.com/"),
    ],
    "switcher": {
        "json_url": f"https://{cname}/versions.json",
        "version_match": get_version_match(__version__),
    },
    "check_switcher": False,
}

# Sphinx extensions
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinx_gallery.gen_gallery",
    "sphinx_autodoc_typehints",
    "numpydoc",
    "sphinx_copybutton",
    "sphinx_click",
    "sphinx_design",
]

# Intersphinx mapping
intersphinx_mapping = {
    "python": ("https://docs.python.org/dev", None),
    "grpc": ("https://grpc.github.io/grpc/python/", None),
    "ansys-tools-common": ("https://common.tools.docs.pyansys.com/version/stable", None),
}

# nitpick exceptions
nitpick_ignore = [
    (
        "py:class",
        "ansys.tools.local_product_launcher.interface.LAUNCHER_CONFIG_T",
    ),  # TypeVar, not a class
    # References that may not resolve due to migration to ansys-tools-common
    ("py:class", "LauncherProtocol"),
    ("py:class", "ProductInstance"),
    ("py:func", "launch_product"),
    ("py:meth", "ProductInstance.stop"),
    ("py:meth", "LauncherProtocol.start"),
    ("py:meth", "LauncherProtocol.stop"),
    ("py:meth", "LauncherProtocol.check"),
    ("py:func", "find_free_ports"),
    ("py:func", "check_grpc_health"),
    ("py:attr", "LauncherProtocol.urls"),
    ("py:obj", "interface.METADATA_KEY_DOC"),
    ("py:obj", "interface.METADATA_KEY_NOPROMPT"),
]

nitpick_ignore_regex = []

# autodoc options
autoclass_content = "class"

# sphinx_autodoc_typehints configuration
typehints_defaults = "comma"
simplify_optional_unions = False

# numpydoc configuration
numpydoc_show_class_members = False
numpydoc_xref_param_type = True

# Consider enabling numpydoc validation. See:
# https://numpydoc.readthedocs.io/en/latest/validation.html#
numpydoc_validate = True
numpydoc_validation_checks = {
    "GL06",  # Found unknown section
    "GL07",  # Sections are in the wrong order.
    "GL08",  # The object does not have a docstring
    "GL09",  # Deprecation warning should precede extended summary
    "GL10",  # reST directives {directives} must be followed by two colons
    "SS01",  # No summary found
    "SS02",  # Summary does not start with a capital letter
    # "SS03", # Summary does not end with a period
    "SS04",  # Summary contains heading whitespaces
    # "SS05", # Summary must start with infinitive verb, not third person
    "RT02",  # The first line of the Returns section should contain only the
    # type, unless multiple values are being returned"
}

# static path
html_static_path = ["_static"]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# The suffix(es) of source filenames.
source_suffix = ".rst"

# The master toctree document.
master_doc = "index"

# sphinx gallery options
sphinx_gallery_conf = {
    # convert rst to md for ipynb
    "pypandoc": True,
    # path to your examples scripts
    "examples_dirs": ["../../examples/example_scripts"],
    # path where to save gallery generated examples
    "gallery_dirs": ["examples"],
    # Pattern to search for example files
    "filename_pattern": r"\.py",
    # Remove the "Download all examples" button from the top level gallery
    "download_all_examples": False,
    # Sort gallery example by file name instead of number of lines (default)
    "within_subsection_order": "FileNameSortKey",
    # directory where function granular galleries are stored
    "backreferences_dir": None,
    # Modules for which function level galleries are created.  In
    "doc_module": "ansys-tools-local-product-launcher",
    "promote_jupyter_magic": True,
    "image_scrapers": ("matplotlib",),
    "ignore_pattern": r"__init__\.py",
    "thumbnail_size": (350, 350),
    "copyfile_regex": r".*\.rst",
}
