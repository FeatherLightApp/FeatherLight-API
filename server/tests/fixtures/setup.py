import os
import sys
import asyncio
import pytest
path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'featherlight'))
print(path)
sys.path.insert(0, path)


from context import GINO, REDIS, LND # noqa
from resolvers.schema import SCHEMA # noqa


@pytest.fixture(scope='session')
def event_loop():
    return asyncio.get_event_loop()


@pytest.fixture(autouse=True, scope='session')
async def schema(event_loop):
    await GINO.initialize()
    await REDIS.initialize()
    await REDIS.conn.flushdb()
    await LND.initialize()
    yield SCHEMA
    await GINO.db.gino.drop_all()
    await GINO.destroy()
    await REDIS.destroy()
    LND.destroy()
