"""configuration file for pytest"""
import pytest
from tests.fixtures.info import info

#inject users list to use created users in multiple tests
def pytest_configure():
    pytest.users = []
