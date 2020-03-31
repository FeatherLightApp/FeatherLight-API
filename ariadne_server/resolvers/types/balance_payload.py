from ariadne import ObjectType
from helpers.async_future import make_async
from context import LND
import rpc_pb2 as ln

_balance_payload = ObjectType('NodeBalance')

@_balance_payload.field('wallet')
async def r_wallet(*_):
    return await LND.stub.WalletBalance(ln.WalletBalanceRequest())


@_balance_payload.field('channel')
async def r_channel(*_):
    return await LND.stub.ChannelBalance(ln.ChannelBalanceRequest())
