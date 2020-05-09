"""resolvers for query types"""
import json
import ast
from ariadne import QueryType
from typing import Union
from grpclib.exceptions import GRPCError
import rpc_pb2 as ln
from context import LND, BITCOIND
from classes.error import Error
from classes.user import User


QUERY = QueryType()


@QUERY.field('info')
# @authenticate
async def r_info(*_) -> dict:
    request = ln.GetInfoRequest()
    return await LND.stub.GetInfo(request)

@QUERY.field('nodeBalance')
@QUERY.field('me')
def r_passthrough(user: User, *_):
    return user


@QUERY.field('decodeInvoice')
async def r_decode_invoice(*_, invoice: str):
    request = ln.PayReqString(pay_req=invoice.replace('lightning:', ''))
    try:
        return await LND.stub.DecodePayReq(request)
    except GRPCError:
        return None

# @QUERY.field('peers')
# async def r_get_peers(_: None, info) -> dict:
#     res = await info.context.bitcoind.req('getpeerinfo')
#     return {
#         'ok': True,
#         'peer_info': res.get('result') or []
#     }
