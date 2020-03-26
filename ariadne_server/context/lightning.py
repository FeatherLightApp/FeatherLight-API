"""module to define lightning stub manager"""
import codecs
import os
import grpc
import rpc_pb2 as ln
import rpc_pb2_grpc as lnrpc
from helpers.async_future import make_async
from helpers.mixins import LoggerMixin


class LightningStub(LoggerMixin):
    """lightning stub manager"""

    def __init__(self):
        self._host = os.environ.get('LND_HOST_PORT')
        self._network = os.environ.get('NETWORK')
        self.id_pubkey = None

        os.environ["GRPC_SSL_CIPHER_SUITES"] = 'HIGH+ECDSA'

        with open(
                f'/root/.lnd/data/chain/bitcoin/{self._network}/admin.macaroon',
                'rb'
        ) as macaroon_bytes:
            macaroon = codecs.encode(macaroon_bytes.read(), 'hex')

        def metadata_callback(_, callback):
            # for more info see grpc docs
            callback([('macaroon', macaroon)], None)

        with open('/root/.lnd/tls.cert', 'rb') as cert_bytes:
            cert = cert_bytes.read()

        cert_creds = grpc.ssl_channel_credentials(cert)
        auth_creds = grpc.metadata_call_credentials(metadata_callback)
        combined_creds = grpc.composite_channel_credentials(
            cert_creds, auth_creds)

        # TODO add wallet unlocking stub for wallet unlock
        # TODO max receive message length? = 1024^3
        channel = grpc.secure_channel(self._host, combined_creds)
        self.logger.info('Initialized LND stub')
        self.stub = lnrpc.LightningStub(channel)

    async def initialize(self):
        """asynchronously init class and populate pupkey"""
        req = ln.GetInfoRequest()
        info = await make_async(self.stub.GetInfo.future(req, timeout=5000))
        self.id_pubkey = info.identity_pubkey
        assert self.id_pubkey
