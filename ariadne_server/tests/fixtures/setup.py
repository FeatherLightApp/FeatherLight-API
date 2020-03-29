import pytest
from context import GINO
from resolvers.schema import SCHEMA

@pytest.fixture(scope='session')
async def setup_db():
    await GINO.initialize()


@pytest.fixture(autouse=True, scope='session')
def schema():
    return SCHEMA
    