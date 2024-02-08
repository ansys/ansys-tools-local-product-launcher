Getting started
---------------

The Local Product Launcher is a utility for launching Ansys products on a local machine
and configuring their settings.

This section explains how to install the Local Product Launcher in user mode and then
how to configure launcher settings for a specific Ansys product and launch it.

.. note::
    If you are interested in contributing to the codebase or documentation for
    the Local Product Launcher, see `Contribute`_.

Installation
''''''''''''

Install the Local Product Launcher in user mode with this command:

.. code::

    pip install ansys-tools-local-product-launcher

To keep Python packages isolated from your system Python, you should use a
`virtual environment <https://docs.python.org/3/library/venv.html>`_.

Configuration
'''''''''''''

Use the ``ansys-launcher`` command-line interface to configure launcher settings
for a specific product. Note that this requires a product plug-in to be installed.

To list the available plug-ins and their launch modes, run this command:

.. code::

    ansys-launcher list-plugins

The output might look like this, where ``ACP`` is the plugin for Ansys Composite PrepPost:

.. code::

    ACP
        direct
        docker_compose

Assuming that the ``ACP`` plug-in is installed, configure the
ACP launcher to use the direct launch mode by running this command:

.. code::

    ansys-launcher configure ACP direct

The command-line tool prompts for the configuration options available for this launcher.

After configuring the launcher, you can inspect the configuration with this command:

.. code::

    ansys-launcher show-config

Or you can edit the configuration file directly. To find the configuration file location, run
this command:

.. code::

    ansys-launcher show-config-path

Launching
'''''''''

To launch the product, run these commands:

.. code:: python

    from ansys.tools.local_product_launcher import launch_product

    server = launch_product("ACP")
