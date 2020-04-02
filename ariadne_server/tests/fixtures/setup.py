import asyncio
import pytest
from context import GINO, REDIS, LND, PUBSUB
from resolvers.schema import SCHEMA


@pytest.fixture(autouse=True, scope='session')
async def schema():
    await GINO.initialize()
    await REDIS.initialize()
    await LND.initialize()
    await PUBSUB.initialize()
    yield SCHEMA
    await GINO.db.gino.drop_all()
    await GINO.destroy()
    await REDIS.destroy()
    await LND.destroy()
    await PUBSUB.destroy()
    