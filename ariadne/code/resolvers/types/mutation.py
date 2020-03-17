from math import floor
import json
from secrets import token_hex
from typing import Union, Optional, Dict
from datetime import (
    datetime,
    timedelta
)
import aioredis
from protobuf_to_dict import protobuf_to_dict
from ariadne import MutationType
from code.classes.user import User
from code.classes.lock import Lock
from code.classes.paym import Paym
from code.classes.error import Error
from code.helpers.async_future import make_async
from code.helpers.mixins import DotDict
from code.helpers.crypto import decode, hash_string
from code.helpers.hexify import hexify
import rpc_pb2 as ln

MUTATION = MutationType()

@MUTATION.field('createUser')
# TODO add post limiter?
async def r_create_user(_: None, info) -> User:
    """create a new user and save to db"""
    #create userid hex
    user = User(token_hex(10))

    user.username = token_hex(10)

    user.password = token_hex(10)

    await info.context.redis.set(f'user_{user.username}_{hash_string(user.password)}', user.userid)

    return user


@MUTATION.field('login')
async def r_auth(_: None, info, username: str, password: str) -> Union[User, Error]:
    if (userid := await info.context.redis.get('user_' + username + '_' + hash_string(password))):
        #pass to union resolver TODO FIXME
        return User(userid.decode('utf-8'))
    return Error(error_type='AuthenticationError', message='Invalid Credentials')

#TODO GET RID OF THIS ITS FOR DEBUG
@MUTATION.field('forceUser')
def r_force_user(_, info, user: str) -> str:
    return User(userid=user)


@MUTATION.field('refreshAccessToken')
async def r_get_token(_: None, info) -> Union[User, Error]:
    # catch scenario of no refresh cookie
    if not (cookie := info.context.req.cookies.get('refresh')):
        return Error(error_type='AuthenticationError', message='No refresh token sent')
    decode_response: Union[Dict, Error] = decode(token=cookie, kind='refresh')
    # pass either error or user instance to union resolver
    info.context.logger.critical(decode_response)
    if isinstance(decode_response, Error):
        return decode_response
    if isinstance(decode_response, Dict):
        return decode_response.get('id')


@MUTATION.field('addInvoice')
# TODO add more flexiblilty in invoice creation
# TODO invoiceFor allows creating invoices for other users on their behalf
# FIXME doesnt work
async def r_add_invoice(user, info, *, memo: str, amt: int, invoiceFor: Optional[str] = None) -> dict:
    """Authenticated route"""
    request = ln.Invoice(
        memo=memo,
        value=amt,
        expiry=3600*24
    )
    response = await make_async(self._lightning.AddInvoice.future(request, timeout=5000))
    output = hexify(protobuf_to_dict(response))
    #change the bytes object to hex string for json serialization
    await self._redis.rpush(f"userinvoices_for_{self.userid}", json.dumps(output))
    # add hex encoded bytes hash to redis
    await self._redis.set(f"payment_hash_{output['r_hash']}", self.userid)
    # response is json protobuf with hex encoded bytes hash
    return output


@MUTATION.field('payInvoice')
async def r_pay_invoice(user: User, info, invoice: str, amt: Optional[int] = None) -> dict:
    """Authenticated Route"""
    assert not amt or amt >= 0
    # obtain a db lock
    lock = Lock(
        info.context.redis,
        'invoice_paying_for_' + user.userid
    )
    if not await lock.obtain_lock():
        info.context.logger.warning('Failed to acquire lock for user {}'.format(user.userid))
        return Error(error_type='PaymentError', message='DB is locked try again later')
    user_balance = await user.balance(info)
    request = ln.PayReqString(pay_req=invoice)
    decoded_invoice = await make_async(info.context.lnd.DecodePayReq.future(request, timeout=5000))
    real_amount = decoded_invoice.num_satoshis if decoded_invoice.num_satoshis > 0 else amt
    decoded_invoice.num_satoshis = real_amount
    info.context.logger.info(f"paying invoice user:{user.userid} with balance {user_balance}, for {real_amount}")
    if not real_amount:
        info.context.logger.warning(f"Invalid amount when paying invoice for user {user.userid}")
        return Error(error_type='Payment Error', message='Invalid invoice amount')
    # check if user has enough balance including possible fees
    if not user_balance >= real_amount + floor(real_amount * 0.01):
        return Error(error_type='Payment Error', message='Not enough balance to pay invoice')

    # determine destination of funds
    if info.context.id_pubkey == decoded_invoice.destination:
        # this is internal invoice now, receiver add balance
        userid_payee = await info.context.redis.get(f"payment_hash_{decoded_invoice.payment_hash}")
        if not userid_payee:
            await lock.release_lock()
            return Error(error_type='Payment Error', message='Could not get user by payment hash')
        if await info.context.redis.get(f"is_paid_{decoded_invoice.payment_hash}"):
            # invoice has already been paid
            await lock.release_lock()
            info.context.logger.warning('Attempted to pay invoice that was already paid')
            return Error(error_type='Payment Error', message='Invoice has already been paid')

        # initialize internal user payee
        payee = User(userid_payee)

        # sender spent his balance
        await user.save_paid_invoice({
            'timestamp': (datetime.utcnow() - datetime(1970, 1, 1)).total_seconds(),
            'type': 'paid_invoice',
            'value': real_amount + floor(real_amount * 0.003),
            'fee': floor(real_amount * 0.003),
            'memo': decoded_invoice.description,
            'pay_req': invoice,
        })
        await info.context.redis.set(f"is_paid_{decoded_invoice.payment_hash}", 1)
        await lock.release_lock()
        decoded_invoice.num_satoshis = real_amount
        return decoded_invoice

    else:
        # this is a standard lightning network payment

        def req_gen():
            # define a request generator that yields a single payment request
            yield ln.SendRequest(
                payment_request=invoice,
                amt=real_amount, # amount is only used for tip invoices,
                fee_limit=ln.FeeLimit(fixed=floor(real_amount * 0.005) + 1)
            )
        await user.lock_funds(info, invoice, decoded_invoice)
        for pay_res in info.context.lnd.SendPayment(req_gen()):
            # stream response synchronously FIXME
            info.context.logger.critical(f"pay res {pay_res}")
            await user.unlock_funds(info, invoice)
            if not pay_res.payment_error and pay_res.payment_preimage:
                # payment success
                pay_dict = protobuf_to_dict(pay_res)
                pay_dict['pay_req'] = invoice
                pay_dict['decoded'] = protobuf_to_dict(decoded_invoice)
                info.context.logger.critical(f"hexified final {hexify(pay_dict)}")

                await info.context.redis.rpush(f"paid_invoices_for_{user.userid}", json.dumps(hexify(pay_dict)))
                await lock.release_lock()
                return pay_res
            else:
                # payment failed
                await lock.release_lock()
                return Error(error_type='PaymentError', message=pay_res.payment_error)
