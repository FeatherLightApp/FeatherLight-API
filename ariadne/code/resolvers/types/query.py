"""resolvers for query types"""
from datetime import (
    datetime,
    timedelta
)
from ariadne import QueryType
import rpc_pb2 as ln
import rpc_pb2_grpc as lnrpc
from code.classes.User import User



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



@query.field('login')
async def r_auth(obj, info, user, pw):
    u = await User.from_credentials(user, pw)
    return r_token_payload(u, info.context)


@query.field('getToken')
async def r_get_token(obj, info):
    cookie = info.context.req.cookies.get(info.context.cookie_name)
    if cookie:
        jsn = info.context.jwt.decode(cookie.encode('utf-8'), kind='refresh')
        u = await User.from_refresh(jsn['token'])
        return r_token_payload(u, info.context)

