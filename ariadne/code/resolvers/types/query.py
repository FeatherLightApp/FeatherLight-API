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
def r_walllet_balance(_, info):
    stub = lnrpc.LightningStub(info.context.channel)
    response = stub.WalletBalance(ln.WalletBalanceRequest())
    return {
        'totalBalance': response.total_balance,
        'confirmedBalance': response.confirmed_balance
    }


@query.field('login')
async def r_auth(*_, user, pw):
    return await User.from_credentials(user, pw)


@query.field('getToken')
async def r_get_token(_, info):
    cookie = info.context.req.cookies.get(info.context.cookie_name)
    if cookie:
        jsn = info.context.jwt.decode(cookie.encode('utf-8'), kind='refresh')
        return await User.from_refresh(ctx=info.context, refresh_token=jsn['token'])
    return None

