"""configuration file for pytest"""
import os

os.environ['POSTGRES_DB'] = 'test'

import pytest
from tests.fixtures.context import context
from tests.fixtures.setup import schema, event_loop
from tests.fixtures.dummy_users import dummy_admin, dummy_user

#inject users list to use created users in multiple tests
def pytest_configure():
    pytest.users = []
