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

@query.field('auth')
async def r_auth(obj, info, user=None, pw=None):
    if not (user and pw) or info.context.req.headers