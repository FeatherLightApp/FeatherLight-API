from ariadne import ObjectType
from helpers.async_future import make_async
from context import LND
import rpc_pb2 as ln

_balance_payload = ObjectType('NodeBalance')

@_balance_payload.field('wallet')
async def r_wallet(*_):
    return await make_async(LND.stub.WalletBalance.future(ln.WalletBalanceRequest()))


@_balance_payload.field('channel')
async def r_channel(*_):
    return await make_async(LND.stub.ChannelBalance.future(ln.ChannelBalanceRequest()))

