"""Module for defining the context class of the application"""
import aioredis
from code.lightning import init_lightning, lnd_tests
from code.bitcoin import Bitcoin
from code.helpers import LoggerMixin
from code.classes import JWT, User

class Context(LoggerMixin):
    """class for passing context values"""

    def __init__(self, config):
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
        self.btcd = Bitcoin(config['btcd'])
        self.logger.warning('initialized context')
        # DEFINE cached variables in global context
        self.cache = {
            'invoce_ispaid': {},
            'list_transactions': None,
            'list_transactions_cache_expiry': 0
        }
        self.jwt = JWT(config['refresh_secret'], config['access_secret'])
        self.cookie_name = config['cookie_name']
    
    def __call__(self, req):
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


    async def user_from_header(self):
        if not 'Authorization' in self.req.headers or not (header := self.req.headers['Authorization']):
            return None
        jsn = self.jwt.decode(
            header.replace('Bearer ', '').encode('utf-8'),
            kind='access'
        )
        return await User.from_auth(
            ctx=self,
            auth=jsn['token']
        )

    # TODO smoke tests for connected containers
    async def smoke_tests(self):
        self.id_pubkey = await lnd_tests()