"""resolvers for query types"""
from math import floor
from datetime import (
    datetime,
    timedelta
)
from secrets import token_hex
from ariadne import QueryType
from jwt.exceptions import ExpiredSignatureError
from protobuf_to_dict import protobuf_to_dict
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
    try:
        if not (u := await User.from_credentials(ctx=info.context, login=user, pw=pw)):
            return 'Invalid Credentials'
        return u
    except ExpiredSignatureError:
        return 'Token has expired'


@query.field('token')
async def r_get_token(_, info):
    if (cookie := info.context.req.cookies.get(info.context.cookie_name)):
        send = cookie.encode('utf-8')
        try:
            jsn = info.context.jwt.decode(send, kind='refresh')
        except ExpiredSignatureError:
            return 'Token has expired'
        return await User.from_auth(ctx=info.context, auth=jsn['token'])
    return 'No refresh token'


@query.field('BTCAddress')
async def r_get_address(_, info):
    if not (u := await info.context.user_from_header()):
        return {
            'ok': False,
            'error': 'Invalid auth token'
        }
    addr = await u.get_address()
    if not addr:
        await u.generate_address()
        addr = await u.get_address()
    return {
        'ok': True,
        'address': addr.decode('utf-8')
    }

@query.field('balance')
async def r_balance(_, info):
    if not (u := await info.context.user_from_header()):
        return {
            'ok': False,
            'error': 'Invalid auth token'
        }
    addr = await u.get_address()
    if not addr:
        await u.generate_address()
    await u.account_for_possible_txids()
    balance = await u.get_balance()
    if (balance < 0):
        balance = 0
    return {
        'ok': True,
        'availableBalance': balance
    }

@query.field('info')
async def r_info(_, info):
    if not (u := await info.context.user_from_header()):
        return {
            'ok': False,
            'error': 'Invalid auth token'
        }
    request = ln.GetInfoRequest()
    response = await fwrap(info.context.lnd.GetInfo.future(request, timeout=5000))
    d = protobuf_to_dict(response)
    if 'chains' in d:
        del d['chains']
    if 'uris' in d:
        del d['uris']
    if 'features' in d:
        del d['features'] #TODO remove these and add the types in gql schema
    return {
        'ok': True,
        **d
    }

@query.field('txs')
async def r_txs(obj, info):
    if not (u =: await info.context.user_from_header()):
        return {
            'ok': False,
            'error': 'Invalid auth token'
        }
    if not await u.get_address():
        u.generate_address()
    await u.account_for_possible_txids()
    txs = await u.get_txs()
    locked_payments = await u.get_locked_payments()
    for locked in locked_payments:
        txs.append({
            'type': 'paid_invoice',
            'fee': floor(locked['amount'] * 0.01),
            'value': locked['amount'] + floor(locked['amount'] * 0.01),
            'timestamp': locked['timestamp'],
            'memo': 'Payment in transition'
        })
    return txs


@query.field('invoices')
async def r_invoices(obj, info, last):
    if not (u =: await info.context.user_from_header()):
        return {
            'ok': False,
            'error': 'Invalid auth token'
        }
    invoices = await u.get_user_invoices()
    return invoices[-1 * last]

@query.field('pending')
async def r_pending(obj, info):
    if not (u =: await info.context.user_from_header()):
        return {
            'ok': False,
            'error': 'Invalid auth token'
        }
    if not await u.get_address():
        await u.generate_address()
    await u.account_for_possible_txids()
    return await u.get_pending_txs()


@query.field('decodeInvoice')
async def r_decode_invoice(obj, info, invoice):
    if not (u =: await info.context.user_from_header()):
        return {
            'ok': False,
            'error': 'Invalid auth token'
        }    
    request = ln.PayReqString(pay_req=invoice)
    res = await fwrap(info.context.lnd.DecodePayReq.future(request, timeout=5000))
    return protobuf_to_dict(res)


@query.field('checkRouteInvoice')
async def r_check_route(obj, info, invoice):
   pass 

