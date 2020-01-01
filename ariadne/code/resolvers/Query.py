"""resolvers for query types"""
import logging
from ariadne import QueryType
import rpc_pb2 as ln
import rpc_pb2_grpc as lnrpc


query = QueryType()

@query.field('echo')
def r_echo(*_, string=None):
    return string

@query.field('walletBalance')
def r_walllet_balance(obj, info):
    stub = lnrpc.LightningStub(info.context.channel)
    response = stub.WalletBalance(ln.WalletBalanceRequest())
    return {
        'totalBalance': response.total_balance,
        'confirmedBalance': response.confirmed_balance
    }

@query.field('genSeed')
def r_gen_seed(obj, info, pw):
    logging.critical(info)
    stub = lnrpc.WalletUnlockerStub(info.context.channel)
    req = ln.GenSeedRequest(
        aezeed_passphrase=pw.encode('utf-8')
    )
    future = stub.GenSeed.future(req)
    logging.critical(type(future))
    res = future.result()
    return res.cipher_seed_mnemonic
