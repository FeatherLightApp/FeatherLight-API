from math import floor
from typing import Union
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
from code.helpers.auth_decorator import authenticate
import rpc_pb2 as ln

MUTATION = MutationType()
# TODO add JWT support and expire tokens in redis

@MUTATION.field('createUser')
# TODO add post limiter?
async def r_create_user(_: None, info) -> User:
    # create blank user
    u = User(ctx=info.context)
    # generate secret credentials
    await u.create()
    # pass to user response resolver
    return u

@MUTATION.field('login')
async def r_auth(_: None, info, username: str, password: str) -> Union[User, Error]:
    return await User.from_credentials(ctx=info.context, username=user, password=password)


@MUTATION.field('refreshAccessToken')
async def r_get_token(_: None, info) -> Union[User, Error]:
    if (cookie := info.context.req.cookies.get('refresh')):
        userResult = await User.from_jwt(ctx=info.context, token=cookie, kind='refresh')
        return userResult
    return Error(error_type='AuthenticationError', message='No refresh token sent')


@MUTATION.field('addInvoice')
@authenticate
# TODO add more flexiblilty in invoice creation
async def r_add_invoice(*_, memo: str, amt: int, user: User) -> dict:
    # response is protobuf with hex encoded bytes hash
    # convert to dict and resolve with default resolver
    response = await user.invoice_manager.add_invoice(memo, amt)
    return protobuf_to_dict(response)


@MUTATION.field('payInvoice')
@authenticate
async def r_pay_invoice(_: None, info, invoice: str, amt: int, user: User) -> dict:
    assert not amt or amt >= 0
    # obtain a db lock
    lock = Lock(
        info.context.redis,
        'invoice_paying_for' + user.userid
    )
    if not await lock.obtain_lock():
        info.context.logger.warning('Failed to acquire lock for user {}'.format(user.userid))
        return Error(error_type='Payment Error', message='DB is locked try again later')
    user_balance = await user.get_calculated_balance()
    request = ln.PayReqString(pay_req=invoice)
    response = await make_async(info.context.lnd.DecodePayReq.future(request, timeout=5000))
    real_amount = response.num_satoshis if response.num_satoshis > 0 else amt
    info.context.logger.info(f'paying invoice user:{user.userid} with balance {user_balance}, for {real_amount}')
    if not real_amount:
        info.context.logger.warning(f'Invalid amount when paying invoice for user {user.userid}')
        return Error(error_type='Payment Error', message='Invalid invoice amount')
    # check if user has enough balance including possible fees
    if not user_balance >= real_amount + floor(real_amount * 0.01):
        return Error(error_type='Payment Error', message='Not enough balance to pay invoice')

    # determine destination of funds
    if info.context.id_pubkey == response.destination:
        # this is internal invoice now, receiver add balance
        userid_payee = await user.get_user_by_payment_hash(response.payment_hash)
        if not userid_payee:
            await lock.release_lock()
            return Error(error_type='Payment Error', message='Could not get user py payment hash')
        if await user.get_payment_hash_paid(response.payment_hash):
            # invoice has already been paid
            await lock.release_lock()
            info.context.logger.warning('Attempted to pay invoice that was already paid')
            return Error(error_type='Payment Error', message='Invoice has already been paid')

        # initialize internal user payee
        payee = User(ctx=info.context)
        payee.userid = userid_payee # TODO fix me this is hackey
        await payee.clear_balance_cache()

        # sender spent his balance
        await user.clear_balance_cache()
        await user.save_paid_invoice({
            'timestamp': (datetime.utcnow() - datetime.datetime(1970, 1, 1)).total_seconds(),
            'type': 'paid_invoice',
            'value': real_amount + floor(real_amount * 0.003),
            'fee': floor(real_amount * 0.003),
            'memo': response.encode('utf-8').hex(),
            'pay_req': invoice,
        })
        await payee.set_payment_hash_paid(response.payment_hash)
        await lock.release_lock()
        response.num_satoshis = real_amount
        return response

    else:
        # this is a standard lightning network payment

        def req_gen():
            # define a request generator that yields a single payment request
            limit = DotDict()
            limit.fixed = floor(response.num_satoshis * 0.005) + 1
            yield ln.SendRequest(
                payment_request=invoice,
                amt=response.num_satoshis, # amount is only used for tip invoices,
                fee_limit=limit
            )
        await user.lock_funds(invoice, response)
        for pay_res in info.context.lnd.SendPayment(req_gen()):
            # stream response synchronously FIXME
            await user.unlock_funds(invoice)
            if pay_res and pay_res.payment_route and pay_res.payment_route.total_amt_msat:
                # payment success
                shallow_paym = Paym(False, False, False) # weird FIXME
                payment = shallow_paym.process_send_payment_response(pay_res)
                payment.pay_req = invoice
                payment.decoded = response
                pay_dict = protobuf_to_dict(payment)
                await user.save_paid_invoice(pay_dict)
                await user.clear_balance_cache()
                await lock.release_lock()
                return payment
            else:
                # payment failed
                await lock.release_lock()
                return Error(error_type='Payment Error', message='Unknown Error has occured')
