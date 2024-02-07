# Copyright (C) 2022 - 2024 ANSYS, Inc. and/or its affiliates.
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

"""
Configuring the launcher from the command line
----------------------------------------------

In this example, the ``example_httpserver`` plugin is configured from the command line.


.. note::

    This example consists mostly of command-line interactions. With the exception of
    interactive commands, it can be run when downloaded as Jupiter notebook.
    The interactive commands and their outputs are simply shown as text.

The configuration contains only a single value ``directory`` which specifies the
directory from which the HTTP server will serve files.

"""

# %%
# To see the list of launch modes for the ``example_httpserver`` product, run:
#
# .. code-block:: bash
#
#   %%bash
#   ansys-launcher configure example_httpserver
#
# The output will be:
#
# ::
#
#   Usage: ansys-launcher configure example_httpserver [OPTIONS] COMMAND [ARGS]...
#
#   Options:
#   --help  Show this message and exit.
#
#   Commands:
#   direct

# %%
# Interactive configuration
# ~~~~~~~~~~~~~~~~~~~~~~~~~
#
# To interactively specify the available configuration options, run:
#
# .. code-block:: bash
#
#   ansys-launcher configure example_httpserver direct
#
# Which may result in a session like:
#
# ::
#
#   directory:
#    [<current-working-directory>]: /path/to/directory
#
#   Updated /home/<your_username>/.config/ansys_tools_local_product_launcher/config.json

# %%
# Non-interactive configuration
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# Alternatively, the configuration can be specified fully from the command line (non-interactively):
#
# .. code-block:: bash
#
#   %%bash
#   ansys-launcher configure example_httpserver direct --directory /path/to/directory
