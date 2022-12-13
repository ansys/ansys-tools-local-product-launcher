# Kickoff notes

Current state of e.g. `launch_mapdl`:
```python
instance = pymapdl.launch_mapdl()

def launch_mapdl():
    if pim.is_configured():
        pim.launch("mapdl")
    # 100s of lines of code to launch locally
```

Goal: replace the per-product code for launching locally.

Proposed user flow:

```bash
pip install pymapdl
```

```
local_pim configure

>>> select product
[1] MAPDL
[2] ACP

1
>>> exe or docker?
exe

>>>
```

--> store into some `config.json`

New `launch_mapdl` implementation:

```python
def launch_mapdl():
    if not pim.is_configured():
        launch_and_configure_local_pim()
    pim.launch('mapdl')
```

## Parts of the system

### Interface definition
```python
class LocalServerInstance:
    ...

def launch(...)

def stop(...)

def check(...)
```

### Helpers

Helper functions for subprocess, docker, docker-compose.

```python
def launch_mapdl_local():
    # some initial setup
    launch_local_helper(...)
```

### Plugin system

Using the generic helper functions, each PyAnsys library implements the generic interface for their own launching needs. This is collected in a plugin system using entrypoints:

E.g. in `pyproject.toml` for PyMAPDL:
```pyproject.toml
[entrypoints]
ansys.tools.local_product_launcher.mapdl.direct = "launch_mapdl_local"
```

### Launcher / server

The "launcher" pulls together the plugins and implements the PIM API server component. Besides being able to read the `config.json`, it should have the ability to launch from an in-code config:

```python
local_pim.launch_pim(config={<config goes here>})
```

### Pytest plugin

Provide pytest fixtures for launching a server during tests:

```python
#conftest.py

@fixture
def start_my_server_while_running_the_test():
    # ...
```
