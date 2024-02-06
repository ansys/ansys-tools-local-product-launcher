..
   Just reuse the root readme to avoid duplicating the documentation.
   Provide any documentation specific to your online documentation
   here.


.. toctree::
    :hidden:
    :maxdepth: 3

    intro
    user_guide/index
    api/index


Ansys Local Product Launcher
============================

A Python utility for launching Ansys products on the local machine, and configure their launch settings.

.. grid:: 1 1 2 2
    :gutter: 2

    .. grid-item-card:: :octicon:`rocket` Getting started
        :link: intro
        :link-type: doc

        Installation, configuration and basic usage.

    .. grid-item-card:: :octicon:`terminal` Command Line Reference
        :link: user_guide/cli
        :link-type: doc

        Reference for the command line tool to configure the Local Product Launcher.

    .. grid-item-card:: :octicon:`plug` Creating a launcher plugin
        :link: user_guide/plugin_creation
        :link-type: doc

        Integrating the Local Product Launcher for your product.

    .. grid-item-card:: :octicon:`code` API reference
        :link: api/index
        :link-type: doc

        Reference for the public Python classes, methods and functions.

    .. grid-item-card:: :octicon:`light-bulb` Rationale
        :columns: 12
        :link: user_guide/rationale
        :link-type: doc

        A look into why the Local Product Launcher was created.
