Creating a Launcher Plugin
--------------------------

This short how-to guide walks you through creating a plugin for the Local Product Launcher. The plugin launches Ansys Composite PrepPost (ACP) as a sub-process.

The Local Product Launcher defines the interface a plugin must satisfy, in the :mod:`.interface` module.

.. note::

    The plugin business logic is kept minimal, to simplify the example.

.. TODO: once merged to main, link to some real plugins in the note above.

Configuration
'''''''''''''

To start, let's define the user-definable configuration for our launcher. Since ACP should be run as a sub-process, the path to the server binary needs to be defined.

This configuration is defined as a `pydantic <https://docs.pydantic.dev>`_ model:

.. code:: python

    import pydantic

    class DirectLauncherConfig(pydantic.BaseModel):
        binary_path: str

The config class inherits from ``pydantic.BaseModel``, and defines a single option ``binary_path`` of type :py:class:`str`.

Launcher
''''''''

Next, we need to define the launcher itself. Below, you can see the full launcher code. There's quite a lot going on there, so each part is then discussed separately.

.. code:: python

    import subprocess

    from ansys.tools.local_product_launcher.interface import LauncherProtocol, ServerType
    from ansys.tools.local_product_launcher.helpers.ports import find_free_ports
    from ansys.tools.local_product_launcher.helpers.grpc import check_grpc_health

    class DirectLauncher(LauncherProtocol[LauncherConfig]):
        CONFIG_MODEL = DirectLauncherConfig
        SERVER_SPEC = {"main": ServerType.GRPC}

        def __init__(self, *, config: DirectLaunchConfig):
            self._config = config
            self._url: str
            self._process: subprocess.Popen[str]

        def start(self) -> None:
            port = find_free_ports()[0]
            self._url = f"localhost:{port}"
            self._process = subprocess.Popen(
                [
                    self._config.binary_path,
                    f"--server-address=0.0.0.0:{port}",
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                text=True,
            )

        def stop(self) -> None:
            self._process.terminate()
            self._process.wait()

        def check(self, timeout: Optional[float] = None) -> bool:
            channel = grpc.insecure_channel(self.urls[ServerKey.MAIN])
            return check_grpc_health(channel=channel, timeout=timeout)

        @property
        def urls(self) -> Dict[str, str]:
            return {"main": self._url}


The launcher class inherits from ``LauncherProtocol[LauncherConfig]``. This isn't a requirement, but if we type-check our code with `mypy <https://mypy.readthedocs.io>`_ it can check that the :class:`.LauncherProtocol` interface is fulfilled.

Next, setting ``CONFIG_MODEL = DirectLauncherConfig`` connects the launcher to the configuration class defined above.

The subsequent line ``SERVER_SPEC = {"main": ServerType.GRPC}`` defines which kind of servers the product starts. Here, there's only a single server, which is accessible via gRPC. The keys in this dictionary can be chosen arbitrarily, but should be consistent across the launcher implementation.
Ideally, you use the key to convey some meaning. For example, ``"main"`` could refer to the main interface to your product, and ``file_transfer`` to an additional service for file up-/download.

The ``__init__`` method

.. code:: python

    def __init__(self, *, config: DirectLaunchConfig):
        self._config = config
        self._url: str
        self._process: subprocess.Popen[str]

must accept exactly one, keyword-only, argument ``config`` that contains the configuration instance.

In this example, we simply store the configuration in the ``_config`` attribute. For ``_url`` and ``_process`` we simply declare their type, for the benefits of the type checker.

Now, we come to the meat of the launcher implementation:

.. code:: python

    def start(self) -> None:
        port = find_free_ports()[0]
        self._url = f"localhost:{port}"
        self._process = subprocess.Popen(
            [
                self._config.binary_path,
                f"--server-address=0.0.0.0:{port}",
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            text=True,
        )

This :meth:`start<.LauncherProtocol.start>` method selects an available port using :func:`.find_free_ports`. It then starts the server as a sub-process. Note that here, we are simply discarding the server output and error. In a real launcher, we should give the option to redirect it, for example to a file.
We also keep track of the URL and port on which the server should be accessible, in the ``_url`` attribute.

Next, we need to implement a way of stopping the process:

.. code:: python

    def stop(self) -> None:
        self._process.terminate()
        self._process.wait()

If your product is prone to ignoring ``SIGTERM``, you might want to add a timeout to :py:meth:`.wait() <subprocess.Popen.wait>`, and re-try with :py:meth:`.kill() <subprocess.Popen.kill>` instead of :py:meth:`.terminate() <subprocess.Popen.terminate>`.

We also need a way to check that the product has successfully launched. This is implemented in :meth:`check <.LauncherProtocol.check>`:

.. code:: python

    def check(self, timeout: Optional[float] = None) -> bool:
        channel = grpc.insecure_channel(self.urls["main"])
        return check_grpc_health(channel=channel, timeout=timeout)

Since the server implements gRPC health checking, we can use the :func:`.check_grpc_health` helper for this purpose.

Finally, the ``_url`` attribute we stored in :meth:`start <.LauncherProtocol.start>` needs to be made available, in the :attr:`urls <.LauncherProtocol.urls>` property:

.. code:: python

    @property
    def urls(self) -> Dict[str, str]:
        return {"main": self._url}

Note that the ``urls`` return value should adhere to the schema defined in ``SERVER_SPEC``.

Entry Point
'''''''''''

Having defined all the necessary components for a Local Product Launcher plugin, we now simply need to register the plugin. This is done through the Python `entrypoints <https://packaging.python.org/specifications/entry-points/>`_ mechanism.

The entrypoint is defined in your package's build configuration. The exact syntax depends on which packaging tool you use:

.. .. grid:: 1
..     :gutter: 3

.. tab-set::

    .. tab-item:: setuptools

        Setuptools can accept its configuration in one of three ways. Choose the one that applies to your project:

        In ``pyproject.toml``:

        .. code:: toml

            [project.entry-points."ansys.tools.local_product_launcher.launcher"]
            "ACP.direct" = "<your.module.name>:DirectLauncher"

        In ``setup.cfg``:

        .. code:: cfg

            [options.entry_points]
            ansys.tools.local_product_launcher.launcher =
                ACP.direct = <your.module.name>:DirectLauncher

        In ``setup.py``:

        .. code:: python

            from setuptools import setup

            setup(
                # ...,
                entry_points = {
                    'ansys.tools.local_product_launcher.launcher': [
                        'ACP.direct = <your.module.name>:DirectLauncher'
                    ]
                }
            )


        See the `setuptools documentation <https://setuptools.pypa.io/en/latest/userguide/entry_point.html#entry-points-for-plugins>`_ for more information.

    .. tab-item:: flit

        In ``pyproject.toml``:

        .. code:: toml

            [project.entry-points."ansys.tools.local_product_launcher.launcher"]
            "ACP.direct" = "<your.module.name>:DirectLauncher"

        See `the flit documentation <https://flit.pypa.io/en/stable/pyproject_toml.html#pyproject-project-entrypoints>`_ for more information.

    .. tab-item:: poetry

        In ``pyproject.toml``:

        .. code:: toml

            [tool.poetry.plugins."ansys.tools.local_product_launcher.launcher"]
            "ACP.direct" = "<your.module.name>:DirectLauncher"

        See the `poetry documentation <https://python-poetry.org/docs/pyproject#plugins>`_ for more information.

In all cases ``ansys.tools.local_product_launcher.launcher`` is an identifier specifying that the entry point defines a Local Product Launcher plugin. It must be kept the same.

The entry point itself has two parts:

- The entry point name ``ACP.direct`` consists of two parts: ``ACP`` is the product name, and ``direct`` is the launch mode identifier. The name must be of this format, and contain exactly one dot ``.`` separating the two parts.
- The entry point value ``<your.module.name>:DirectLauncher`` defines where the launcher implementation is located. In other words

  .. code:: python

      from <your.module.name> import DirectLauncher

  must load the launcher class.

You need to re-install your package (even if installed with ``pip install -e``) for the entry points to update.

CLI Defaults and Description
''''''''''''''''''''''''''''

With the three parts outlined above, you've successfully created a Local Product Launcher plugin. :octicon:`rocket`

Finally, we can improve the usability of the command line by adding a default and description to the configuration class.

To do so, we edit our ``DirectLaunchConfig`` class, assigning a ``pydantic.Field`` to the ``binary_path`` class attribute.


.. code:: python

    import os

    import pydantic

    from ansys.tools.local_product_launcher.helpers.ansys_root import get_ansys_root


    def get_default_binary_path() -> Union[str, pydantic.fields.UndefinedType]:
        try:
            ans_root = get_ansys_root()
            binary_path = os.path.join(ans_root, "ACP", "acp_grpcserver")
            if os.name == "nt":
                binary_path += ".exe"
            return binary_path
        except (RuntimeError, FileNotFoundError):
            return pydantic.fields.Undefined


    class DirectLaunchConfig(pydantic.BaseModel):
        binary_path: str = pydantic.Field(
            default=get_default_binary_path(), description="Path to the ACP gRPC server executable."
        )


For the default value, we use the :func:`.get_ansys_root` helper to find the Ansys installation directory.

Now, the user can see the description when running ``ansys-launcher configure ACP direct``, and simply accept the default value if they wish.
