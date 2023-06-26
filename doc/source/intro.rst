Getting started
---------------


Installation
''''''''''''

Install the Local Product Launcher with:

.. code::

    pip install ansys-tools-local-product-launcher

We recommend using a `virtual environment <https://docs.python.org/3/library/venv.html>`_
to keep Python packages isolated from your system Python.


Configuration
'''''''''''''

Use the ``ansys-launcher`` command line interface to configure launcher settings for a specific product. Note that this requires a product plug-in to be installed.

For example, assuming that the ``ACP`` plug-in is installed:

.. code::

    ansys-launcher configure ACP direct

The CLI prompts for the configuration options available for this launcher.


Launching
'''''''''

To launch the product:

.. code:: python

    from ansys.tools.local_product_launcher import launch_product

    server = launch_product("ACP")
