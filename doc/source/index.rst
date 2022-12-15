..
   Just reuse the root readme to avoid duplicating the documentation.
   Provide any documentation specific to your online documentation
   here.


.. toctree::
    :hidden:
    :maxdepth: 3

    intro
    plugin_creation
    api/index
    cli


Ansys Local Product Launcher
============================

A Python utility for launching Ansys products on the local machine, and configure their launch settings.

.. grid:: 1 1 2 2
    :gutter: 2

    .. grid-item-card:: :octicon:`rocket` Getting Started
        :link: intro
        :link-type: doc

        Installation, configuration and basic usage.

    .. grid-item-card:: :octicon:`plug` Creating a Launcher Plugin
        :link: plugin_creation
        :link-type: doc

        Integrating the Local Product Launcher for your product.

    .. grid-item-card:: :octicon:`code` API Reference
        :link: api/index
        :link-type: doc

        Reference for the public Python classes, methods and functions.

    .. grid-item-card:: :octicon:`terminal` Command Line Reference
        :link: cli
        :link-type: doc

        Reference for the command line tool to configure the Local Product Launcher.
