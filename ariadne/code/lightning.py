"""Initializes lighning stub"""
import codecs
import os
import grpc
import rpc_pb2 as ln
import rpc_pb2_grpc as lnrpc

def init_lightning(host):
    os.environ["GRPC_SSL_CIPHER_SUITES"] = 'HIGH+ECDSA'

    with open('/root/.lnd/data/chain/bitcoin/simnet/admin.macaroon', 'rb') as m:
        macaroon = codecs.encode(m.read(), 'hex')

    def metadata_callback(context, callback):
        # for more info see grpc docs
        callback([('macaroon', self.macaroon)], None)

    with open('/root/.lnd/tls.cert', 'rb') as c:
        cert = c.read()

    cert_creds = grpc.ssl_channel_credentials(cert)
    auth_creds = grpc.metadata_call_credentials(metadata_callback)
    combined_creds = grpc.composite_channel_credentials(cert_creds, auth_creds)

    # TODO add wallet unlocking stub for wallet unlock
    # TODO max receive message length? = 1024^3
    channel = grpc.secure_channel(host, combined_creds)
    return lnrpc.LightningStub(channel)
