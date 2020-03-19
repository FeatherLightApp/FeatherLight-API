"""Module for defining the context class of the application"""
import json
import aioredis
from starlette.requests import Request
from helpers.mixins import LoggerMixin
from helpers.async_future import make_async

import codecs
import os
import grpc
import rpc_pb2 as ln
import rpc_pb2_grpc as lnrpc

from secrets import token_hex
from httpx import AsyncClient
from helpers.mixins import LoggerMixin

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

    async def destroy(self):
        self.logger.info('destroying redis')
        self.conn.close()
        await self.conn.wait_closed()


class BitcoinClient(AsyncClient, LoggerMixin):
    """Subclass for making btcd rpc requests"""
    def __init__(self, config):
        self._host = config['host']
        self._port = config['port']
        self._user = config['user']
        self._pass = config['pass']

    async def req(self, method: str, params=None, reqid=None):
        """make a request to bitcoin rpc and return response json"""
        url = f'http://{self._host}:{self._port}'
        js = {'method': method}
        if params:
            js['params'] = params
        js['id'] = reqid if reqid else token_hex(4)
        async with AsyncClient() as client:
            res = await client.post(
                url,
                json=js,
                auth=(self._user, self._pass),
                headers={'Content-Type': 'application/json'}
            )
            return res.json()


_config = json.loads(open('app_config.json').read())

REDIS = RedisConnection(_config['redis']['host'], None, None)
LND = LightningStub(_config['lnd']['host'], _config['network'])
BITCOIND = BitcoinClient(_config['bitcoind'])
