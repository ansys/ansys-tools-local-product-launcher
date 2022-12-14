import pytest

from ansys.tools.local_product_launcher import config


@pytest.fixture(autouse=True)
def reset_config():
    """Reset the configuration at the start of each test."""
    config.reset_config()
