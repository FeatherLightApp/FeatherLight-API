"""configuration file for pytest"""
import pytest
from tests.fixtures.info import info
from tests.fixtures.setup import schema, setup_db

#inject users list to use created users in multiple tests
def pytest_configure():
    pytest.users = []
