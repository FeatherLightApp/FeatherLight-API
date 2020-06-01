from ariadne import ObjectType
from context import LND
from proto import rpc_pb2 as ln

NODE_BALANCE = ObjectType("NodeBalance")


@NODE_BALANCE.field("wallet")
async def r_wallet(*_):
    return await LND.stub.WalletBalance(ln.WalletBalanceRequest())


@NODE_BALANCE.field("channel")
async def r_channel(*_):
    return await LND.stub.ChannelBalance(ln.ChannelBalanceRequest())


@NODE_BALANCE.field("liquidity")
async def r_liquidity(*_):
    req = ln.ListChannelsRequest(public_only=True)
    channels = (await LND.stub.ListChannels(req)).channels
    return {
        "inbound": sum(x.remote_balance - x.remote_chan_reserve_sat for x in channels),
        "outbound": sum(x.local_balance - x.local_chan_reserve_sat for x in channels),
    }
