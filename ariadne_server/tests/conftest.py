"""configuration file for pytest"""
import pytest
from tests.fixtures.context import context
from tests.fixtures.setup import schema

#inject users list to use created users in multiple tests
def pytest_configure():
    pytest.users = []
