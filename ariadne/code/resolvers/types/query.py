"""resolvers for query types"""
from datetime import (
    datetime,
    timedelta
)
from ariadne import QueryType
import rpc_pb2 as ln
import rpc_pb2_grpc as lnrpc
from code.classes.User import User
from code.helpers.async_future import fwrap


query = QueryType()

@query.field('echo')
def r_echo(*_, string=None):
    return string


@query.field('walletBalance')
async def r_walllet_balance(_, info):
    response = await fwrap(info.context.lnd.WalletBalance.future(ln.WalletBalanceRequest()))
    return {
        'totalBalance': response.total_balance,
        'confirmedBalance': response.confirmed_balance
    }


@query.field('login')
async def r_auth(obj, info, user, pw):
    return await User.from_credentials(ctx=info.context, login=user, pw=pw)


@query.field('getToken')
async def r_get_token(_, info):
    cookie = info.context.req.cookies.get(info.context.cookie_name)
    if cookie:
        send = cookie.encode('utf-8')
        jsn = info.context.jwt.decode(send, kind='refresh')
        return await User.from_refresh(ctx=info.context, refresh_token=jsn['token'])
    return None

