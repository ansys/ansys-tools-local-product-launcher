HTTP Server launcher plugin
---------------------------

This example shows the launcher plugin used to start the Python HTTP server. The full source
is available in the `examples/example_httpserver_plugin directory <https://github.com/ansys-internal/ansys-tools-local-product-launcher/tree/main/examples/example_httpserver_plugin>`_
on GitHub.

Here, we will show some aspects of this code. The concepts behind this code are explained in
the :ref:`plugin creation guide <plugin_creation>`.

Launcher code
~~~~~~~~~~~~~

The ``LauncherConfig`` class determines which options are available to the user when configuring the launcher. We expose
a single option ``directory``, which determines which directory the server will serve files from.

.. include:: ../../../examples/example_httpserver_plugin/src/example_httpserver_plugin/launcher.py
    :literal:
    :start-after: # START_LAUNCHER_CONFIG
    :end-before: # END_LAUNCHER_CONFIG


The ``Launcher`` class actually starts the server. It needs to fulfill the interface defined by the
:class:`.LauncherProtocol` class. Namely:

- the ``start``, and ``stop`` method for starting and stopping the server
- the ``check`` method for checking if the server is running
- the ``urls`` property for getting the URLs on which the server is serving requests

.. include:: ../../../examples/example_httpserver_plugin/src/example_httpserver_plugin/launcher.py
    :literal:
    :start-after: # START_LAUNCHER_CLS
    :end-before: # END_LAUNCHER_CLS

The local product launcher will use this minimal interface to construct a :class:`.ProductInstance`, which adds some additional
functionality on top. For example, the ``ProductInstance`` class will automatically stop the server when the Python process
terminates.


Entrypoint configuration
~~~~~~~~~~~~~~~~~~~~~~~~

Besides the launcher code, the plugin needs to be registered by adding an entrypoint to
the ``pyproject.toml`` file, as described in :ref:`the entrypoint section <entrypoint>`
of the plugin creation guide. In this example, we use ``flit`` as a build tool, so the
``pyproject.toml`` file looks like this:


.. include:: ../../../examples/example_httpserver_plugin/pyproject.toml
    :literal:

Two entry points for the local product launcher are defined:

- ``direct`` - a launch mode which can be configured by the user
- ``__fallback__`` - a fallback mode which is used if no configuration is available

Both use the same launcher class.
