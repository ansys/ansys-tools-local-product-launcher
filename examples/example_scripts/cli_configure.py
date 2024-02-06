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

#%%
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

#%%
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

#%%
# Non-interactive configuration
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# Alternatively, the configuration can be specified fully from the command line (non-interactively):
#
# .. code-block:: bash
#
#   %%bash
#   ansys-launcher configure example_httpserver direct --directory /path/to/directory
