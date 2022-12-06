from ansys.utilities.local_instancemanager_server import __version__


def test_pkg_version():
    assert __version__ == "0.1.dev0"
