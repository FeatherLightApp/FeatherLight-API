import codecs
import grpc
import rpc_pb2 as ln
import rpc_pb2_grpc as lnrpc


os.environ["GRPC_SSL_CIPHER_SUITES"] = 'HIGH+ECDSA'

with open('/root/.lnd/data/chain/bitcoin/simnet/admin.macaroon', 'rb') as m:
    macaroon = codecs.encode(m.read(), 'hex')

def metadata_callback(context, callback):
    # for more info see grpc docs
    callback([('macaroon', self.macaroon)], None)

with open('/root/.lnd/tls.cert', 'rb') as c:
    cert = c.read()

cert_creds = grpc.ssl_channel_credentials(self.cert)
auth_creds = grpc.metadata_call_credentials(metadata_callback)
combined_creds = grpc.composite_channel_credentials(cert_creds, auth_creds)

# TODO add wallet unlocking stub for wallet unlock

channel = grpc.secure_channel('lnd:10009', combined_creds, 'grpc.max_receive_message_length'=1024 * 1024 * 1024)
stub = lnrpc.LightningStub(channel)