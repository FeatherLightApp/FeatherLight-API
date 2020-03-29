import pytest
from context import GINO, REDIS, LND
from resolvers.schema import SCHEMA

@pytest.fixture(scope='session')
async def setup_db():
    print('initializing connections for testing')
    await GINO.initialize()
    await REDIS.initialize()
    await LND.initialize()


@pytest.fixture(autouse=True, scope='session')
def schema():
    return SCHEMA
    