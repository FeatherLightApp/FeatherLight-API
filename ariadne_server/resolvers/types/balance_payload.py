from ariadne import ObjectType

_balance_response = ObjectType('NodeBalance')

@_balance_response.field('wallet')
async def r_wallet(*_):
    return await make_async(LND.stub.WalletBalance.future(ln.WalletBalanceRequest()))


@_balance_response.field('channel')
async def r_channel(*_):
    return await make_async(LND.stub.ChannelBalance.future(ln.ChannelBalanceRequest()))

