"""Module for defining the context class of the application"""
import aioredis
import pytest
from starlette.requests import Request
from code.init_lightning import init_lightning, lnd_tests
from code.helpers.mixins import LoggerMixin
from code.classes.jwt import JWT
from code.classes.user import User
from code.classes.bitcoin import BitcoinClient


class Context(LoggerMixin):
    """class for passing context values"""

    def __init__(self, config: dict):
        super().__init__()
        self.logger.info(config)
        self._config = config
        self.req = None
        self.redis = None
        self.lnd = init_lightning(
            host=config['lnd']['grpc'],
            network=config['network']
        )
        self.id_pubkey = None
        self.btcd = BitcoinClient(config['btcd'])
        self.logger.warning('initialized context')
        # DEFINE cached variables in global context
        self.cache = {
            'invoce_ispaid': {},
            'list_transactions': None,
            'list_transactions_cache_expiry': 0
        }
        self.jwt = JWT(config['refresh_secret'], config['access_secret'])
        self.cookie_name = config['cookie_name']
    
    def __call__(self, req: Request):
        self.req = req
        return self

    async def init_redis(self):
        """async init redis db. call before app startup"""
        self.logger.warning('instantiating redis')
        self.redis = await aioredis.create_redis_pool(self._config['redis']['host'])


    async def destroy(self):
        """Destroy close necessary connections gracefully"""
        self.logger.info('Destroying redis instance')
        self.redis.close()
        await self.redis.wait_closed()

    # TODO smoke tests for connected containers
    async def smoke_tests(self):
        self.id_pubkey = await lnd_tests()