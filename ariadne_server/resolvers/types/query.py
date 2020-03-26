"""resolvers for query types"""
import json
import ast
from ariadne import QueryType
from protobuf_to_dict import protobuf_to_dict
import rpc_pb2 as ln
from helpers.async_future import make_async
from context import LND, BITCOIND


QUERY = QueryType()


@QUERY.field('me')
def r_me(obj, *_):
    #pass object into union resolver
    return obj


@QUERY.field('walletBalance')
async def r_wallet_balance(*_) -> dict:
    return await make_async(LND.stub.WalletBalance.future(ln.WalletBalanceRequest()))


@QUERY.field('info')
# @authenticate
async def r_info(*_) -> dict:
    request = ln.GetInfoRequest()
    response = await make_async(LND.stub.GetInfo.future(request, timeout=5000))
    d = protobuf_to_dict(response)
    if 'chains' in d:
        del d['chains']
    if 'uris' in d:
        del d['uris']
    if 'features' in d:
        del d['features']  # TODO remove these and add the types in gql schema
    return {
        'ok': True,
        **d
    }

# @QUERY.field('txs')
# #@authenticate
# async def r_txs(_: None, info, *, user: User) -> dict:
#     address = await user.btc_address()
#     await user.account_for_possible_txids()
#     txs = await user.get_txs()
#     locked_payments = await user.get_locked_payments()
#     for locked in locked_payments:
#         txs.append({
#             'type': 'paid_invoice',
#             'fee': floor(locked['amount'] * 0.01),
#             'value': locked['amount'] + floor(locked['amount'] * 0.01),
#             'timestamp': locked['timestamp'],
#             'memo': 'Payment in transition'
#         })
#     return txs


# @QUERY.field('invoices')
# #@authenticate
# async def r_invoices(_: None, info, *, last: Optional[int], user: User):
#     invoices = await user.get_user_invoices()
#     return invoices[-1 * last]

# @QUERY.field('pending')
# #@authenticate
# async def r_pending(obj, info, **kwargs):
#     address = await user.get_address()
#     await user.account_for_possible_txids()
#     return await user.get_pending_txs()


# @authenticate
@QUERY.field('decodeInvoice')
async def r_decode_invoice(*_, invoice: str) -> dict:
    request = ln.PayReqString(pay_req=invoice)
    res = await make_async(LND.stub.DecodePayReq.future(request, timeout=5000))
    return {
        'ok': True,
        **protobuf_to_dict(res)
    }


# @QUERY.field('peers')
# async def r_get_peers(_: None, info) -> dict:
#     res = await info.context.bitcoind.req('getpeerinfo')
#     return {
#         'ok': True,
#         'peer_info': res.get('result') or []
#     }

# TODO remove temp query for generic rpc
@QUERY.field('genericRPC')
async def r_rpc_call(*_, command: str, params: str = '') -> str:
    param_dict = None if not params else ast.literal_eval(params)
    res = await BITCOIND.req(command, params=param_dict)
    return json.dumps(res)

# @query.field('checkRouteInvoice')
# @authenticate
# async def r_check_route(obj, info, invoice):
# TODO
