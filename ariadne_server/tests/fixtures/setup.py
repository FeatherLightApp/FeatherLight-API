import asyncio
import pytest
from context import GINO, REDIS, LND
from resolvers.schema import SCHEMA


@pytest.fixture(autouse=True, scope='session')
async def schema(event_loop):
    await GINO.initialize()
    await REDIS.initialize()
    await LND.initialize()
    yield SCHEMA
    await GINO.db.gino.drop_all()
    await GINO.destroy()
    await REDIS.destroy()
    await LND.destroy()
    