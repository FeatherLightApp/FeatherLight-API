import asyncio
import pytest
from context import GINO, REDIS, LND, PUBSUB
from resolvers.schema import SCHEMA

@pytest.yield_fixture(autouse=True, scope='session')
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.yield_fixture(autouse=True, scope='session')
async def schema(event_loop):
    await GINO.initialize()
    await REDIS.initialize()
    await LND.initialize()
    PUBSUB.initialize()
    yield SCHEMA
    await GINO.db.gino.drop_all()
    await GINO.destroy()
    await REDIS.destroy()
    await LND.destroy()
    await PUBSUB.destroy()
    