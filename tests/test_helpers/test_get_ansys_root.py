import pytest

from ansys.tools.local_product_launcher.helpers.ansys_root import get_ansys_root


def test_raises_on_inexistent_version():
    with pytest.raises(FileNotFoundError):
        get_ansys_root(release_version="999")


@pytest.mark.xfail(
    reason=(
        "This test can only pass if an Ansys installation is present on "
        "the machine, and the AWP_ROOT* env variable is set."
    )
)
def test_get_root():
    get_ansys_root()


@pytest.mark.xfail(
    reason="This test can only pass if an Ansys v232 installation is present on the machine."
)
def test_get_root_from_version():
    get_ansys_root(release_version="232")
