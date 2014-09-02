import pytest


def pytest_runtest_setup(item):
    if not item.config.getoption("--external"):
        pytest.skip("need --external option to run")
