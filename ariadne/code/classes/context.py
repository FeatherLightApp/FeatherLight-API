"""Module for defining the context class of the application"""
import json
import aioredis
import pytest
from starlette.requests import Request
from code.helpers.mixins import LoggerMixin
from code.classes.bitcoin import BitcoinClient
from code.helpers.async_future import make_async

import codecs
import os
import grpc
import rpc_pb2 as ln
import rpc_pb2_grpc as lnrpc

#TODO remove along with context singleton in favor of global connection instances
def init_lightning(host, network):
    os.environ["GRPC_SSL_CIPHER_SUITES"] = 'HIGH+ECDSA'

    with open(f'/root/.lnd/data/chain/bitcoin/{network}/admin.macaroon', 'rb') as m:
        macaroon = codecs.encode(m.read(), 'hex')

    def metadata_callback(context, callback):
        # for more info see grpc docs
        callback([('macaroon', macaroon)], None)

    with open('/root/.lnd/tls.cert', 'rb') as c:
        cert = c.read()

    cert_creds = grpc.ssl_channel_credentials(cert)
    auth_creds = grpc.metadata_call_credentials(metadata_callback)
    combined_creds = grpc.composite_channel_credentials(cert_creds, auth_creds)

    # TODO add wallet unlocking stub for wallet unlock
    # TODO max receive message length? = 1024^3
    channel = grpc.secure_channel(host, combined_creds)
    return lnrpc.LightningStub(channel)

#Deprecate infavor of global varibles
class Context(LoggerMixin):
    """class for passing context values"""

    def __init__(self, config: dict):
        LoggerMixin().__init__()
        self.logger.info(config)
        self._config = config
        self.req = None #populated on each server request
        self.redis = None
        self.lnd = init_lightning(
            host=config['lnd']['host'],
            network=config['network']
        )
        self.id_pubkey = None
        self.bitcoind = BitcoinClient(config['bitcoind'])
        self.logger.warning('initialized context')
        # DEFINE cached variables in global context
    
    def __call__(self, req: Request):
        self.req = req
        return self

    async def async_init(self):
        """async init redis db. call before app startup"""
        self.logger.warning('instantiating redis')
        self.redis = await aioredis.create_redis_pool(self._config['redis']['host'])
        self.logger.warning(self.redis)


    async def destroy(self):
        """Destroy close necessary connections gracefully"""
        self.logger.info('Destroying redis instance')
        self.redis.close()
        await self.redis.wait_closed()

    # TODO smoke tests for connected containers
    async def smoke_tests(self):
        pass


class LightningStub(LoggerMixin):

    def __init__(self, host, network):
        self._host = host
        self._network = network
        self.id_pubkey = None

        os.environ["GRPC_SSL_CIPHER_SUITES"] = 'HIGH+ECDSA'

        with open(f'/root/.lnd/data/chain/bitcoin/{self._network}/admin.macaroon', 'rb') as m:
            macaroon = codecs.encode(m.read(), 'hex')

        def metadata_callback(context, callback):
            # for more info see grpc docs
            callback([('macaroon', macaroon)], None)

        with open('/root/.lnd/tls.cert', 'rb') as c:
            cert = c.read()

        cert_creds = grpc.ssl_channel_credentials(cert)
        auth_creds = grpc.metadata_call_credentials(metadata_callback)
        combined_creds = grpc.composite_channel_credentials(cert_creds, auth_creds)

        # TODO add wallet unlocking stub for wallet unlock
        # TODO max receive message length? = 1024^3
        channel = grpc.secure_channel(self._host, combined_creds)
        self.logger.info('Initialized LND stub')
        self.stub = lnrpc.LightningStub(channel)

    async def initialize(self):
        req = ln.GetInfoRequest()
        info = await make_async(self.stub.GetInfo.future(req, timeout=5000))
        self.id_pubkey = info.identity_pubkey
        assert self.id_pubkey

_config = json.loads(open('code/app_config.json').read())

LND = LightningStub(_config['lnd']['host'], _config['network'])


class RedisConnection(LoggerMixin):

    def __init__(self, host, username, password):
        self.conn = None
        self._host = host
        self._username = username
        self._password = password

    async def initialize(self):
        self.logger.info('Initializing redis connection')
        # TODO add support for redis username and passord
        self.conn = await aioredis.create_redis_pool(self._host)


REDIS = RedisConnection(_config['redis']['host'], None, None)