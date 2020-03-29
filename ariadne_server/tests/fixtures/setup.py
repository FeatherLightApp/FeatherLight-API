import pytest
from context import GINO, REDIS, LND
from resolvers.schema import SCHEMA


@pytest.fixture(autouse=True, scope='session')
async def schema():
    await GINO.initialize()
    await REDIS.initialize()
    await LND.initialize()
    yield SCHEMA
    await GINO.destroy()
    await REDIS.destroy()
    