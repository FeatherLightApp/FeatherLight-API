"""configuration file for pytest"""
import os

os.environ['POSTGRES_DB'] = 'test'

from .fixtures.fake_context import context # noqa
from .fixtures.setup import schema, event_loop # noqa
from .fixtures.dummy_users import dummy_admin, dummy_user # noqa

os.chdir(os.path.dirname(__file__))