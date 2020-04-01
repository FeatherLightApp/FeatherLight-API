"""module to define lightning stub manager"""
import ssl
import codecs
import os
from grpclib.client import Channel
from grpclib.events import SendRequest, listen
import rpc_pb2 as ln
import rpc_grpc as lnrpc
from helpers.async_future import make_async
from helpers.mixins import LoggerMixin



class LightningStub(LoggerMixin):
    """lightning stub manager"""

    def __init__(self):
        self._host = os.environ.get('LND_HOST')
        self._port = int(os.environ.get('LND_PORT'))
        self._network = os.environ.get('NETWORK')
        self.id_pubkey = None
        self.stub = None

        os.environ["GRPC_SSL_CIPHER_SUITES"] = 'HIGH+ECDSA'
        os.environ['SSL_CERT_DIR'] = '/root/.lnd'

        with open(
                f'/root/.lnd/data/chain/bitcoin/{self._network}/admin.macaroon',
                'rb'
        ) as macaroon_bytes:
            self._macaroon = codecs.encode(macaroon_bytes.read(), 'hex')

        self.logger.critical(ssl.get_default_verify_paths())

        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS)
        ctx.set_default_verify_paths('/root/.lnd')
        ctx.verify_mode = ssl.CERT_REQUIRED
        ctx.load_verify_locations(cafile='/root/.lnd/tls.cert')
        ctx.load_cert_chain('/root/.lnd/tls.cert', '/root/.lnd/tls.key') # can take second arg path the private key str(client_key)
        #ctx.load_verify_locations(str(trusted)) WE TRUST THE CERTIFICATE
        ctx.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1
        ctx.set_ciphers('ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20')
        ctx.set_alpn_protocols(['h2'])
        try:
            ctx.set_npn_protocols(['h2'])
        except NotImplementedError:
            pass
        self._channel = Channel(self._host, self._port, ssl=ctx)

        async def attach_metadata(event: SendRequest):
            event.metadata['macaroon'] = self._macaroon

        listen(self._channel, SendRequest, attach_metadata)


    async def initialize(self):
        """asynchronously init class and populate pubkey"""

        # TODO add wallet unlocking stub for wallet unlock
        # TODO max receive message length? = 1024^3
        self.logger.info('Initialized LND stub')
        self.stub = lnrpc.LightningStub(self._channel)
        req = ln.GetInfoRequest()
        info = await self.stub.GetInfo(req)
        self.id_pubkey = info.identity_pubkey
        assert self.id_pubkey

    async def destroy(self):
        await self._channel.close()
