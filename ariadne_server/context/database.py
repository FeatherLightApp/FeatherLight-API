import os
import asyncio
from socket import gaierror
from gino import Gino
from helpers.mixins import LoggerMixin


class GinoInstance(LoggerMixin):
    """Gino connection manager"""

    def __init__(self):
        self._host = os.environ.get('POSTGRES_HOST')
        self._user = os.environ.get('POSTGRES_USER')
        self._password = os.environ.get('POSTGRES_PASSWORD')
        self._db_name = os.environ.get('POSTGRES_DB')
        self.db = Gino()

    async def initialize(self):
        """init db connection"""
        bind_str = f"postgresql://{self._user}:{self._password}@{self._host}/{self._db_name}"
        i = 1
        while True:
            try:
                self.logger.warning(f'connecting to: {bind_str}, attempt {i}')
                await self.db.set_bind(bind_str)
                self.logger.warning('bound to db')
                await self.db.gino.create_all()
                self.logger.info('success')
                break
            except gaierror as e:
                self.logger.warning(e)
                self.logger.warning(f'DB connect attempt {i} failed')
                await asyncio.sleep(5)
                i += 1

    async def destroy(self):
        """ close connection"""
        await self.db.pop_bind().close()
