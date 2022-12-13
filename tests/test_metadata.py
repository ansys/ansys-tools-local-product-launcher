from ansys.tools.local_product_launcher import __version__


def test_pkg_version():
    assert __version__ == "0.1.dev0"
