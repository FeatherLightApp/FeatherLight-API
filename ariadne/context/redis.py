import os
import aioredis
from helpers.mixins import LoggerMixin

class RedisConnection(LoggerMixin):

    def __init__(self):
        self.conn = None
        self._host = os.environ.get('REDIS_HOST')
        self._username = None
        self._password = None

    async def initialize(self):
        self.logger.info('Initializing redis connection')
        # TODO add support for redis username and passord
        self.conn = await aioredis.create_redis_pool(self._host)

    async def destroy(self):
        self.logger.info('destroying redis')
        self.conn.close()
        await self.conn.wait_closed()
