"""define app entry point"""
import os
from json import loads
import aioredis
import rpyc
from starlette.applications import Starlette
from ariadne.asgi import GraphQL
from code.resolvers.schema import schema
from code.lightning import init_lightning
from code.helpers.mixins import LoggerMixin
from code.classes.JWT import JWT


# TODO import and run environment tests

# end tests



class Context(LoggerMixin):
    """class for passing context values"""

    def __init__(self, config):
        super().__init__()
        self._config = config
        self.req = None
        self.redis = None
        self.lightning = init_lightning(self._config['lnd']['grpc'])
        self.bitcoind = rpyc.connect(
            self._config['btcd']['host'],
            self._config['btcd']['port']
        )
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


conf = loads(open('code/app_config.json').read())
keys = loads(open('/code/keys.json').read())

conf.update(keys)

ctx = Context(conf)

app = Starlette(debug=True, on_startup=[ctx.init_redis])
app.mount('/graphql', GraphQL(schema, debug=True, context_value=ctx))
