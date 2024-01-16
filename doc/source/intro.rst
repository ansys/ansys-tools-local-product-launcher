Getting started
---------------


Installation
''''''''''''

Install the Local Product Launcher with:

.. code::

    pip install ansys-tools-local-product-launcher

It is recommended to use a `virtual environment <https://docs.python.org/3/library/venv.html>`_
to keep Python packages isolated from your system Python.


Configuration
'''''''''''''

Use the ``ansys-launcher`` command line interface to configure launcher settings for a specific product. Note that this requires a product plug-in to be installed.

You can list the available plug-ins and their launch modes with

.. code::

    ansys-launcher list-plugins

The output might look like:

.. code::

    ACP
        direct
        docker_compose

To configure the ACP launcher to use the direct launch mode, use:

.. code::

    ansys-launcher configure ACP direct

The command line tool prompts for the configuration options available for this launcher.

After configuring the launcher, you can inspect the configuration with:

.. code::

    ansys-launcher show-config

Or you can edit the configuration file directly. The configuration file location can
be found with:

.. code::

    ansys-launcher show-config-path


Launching
'''''''''

To launch the product:

.. code:: python

    from ansys.tools.local_product_launcher import launch_product

    server = launch_product("ACP")
