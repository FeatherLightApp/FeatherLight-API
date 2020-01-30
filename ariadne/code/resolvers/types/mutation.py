from math import floor
from datetime import (
    datetime,
    timedelta
)
import aioredis
from protobuf_to_dict import protobuf_to_dict
from ariadne import MutationType
from code.classes import User, Lock, Paym
from code.helpers import make_async, DotDict
import rpc_pb2 as ln

mutation = MutationType()
# TODO add JWT support and expire tokens in redis

@mutation.field('create')
# TODO add post limiter?
async def r_create(_, info):
    u = User(
        ctx=info.context
    )
    await u.create()
    return {
        'ok': True,
        'login': u.login,
        'password': u.pw
    }

@mutation.field('addInvoice')
async def r_add_invoice(_, info, memo, amt):
    if not (u := await info.context.user_from_header()):
        return {
            'ok': False,
            'error': 'Invalid auth token'
        }
    response = await u.add_invoice(memo, amt)
    return protobuf_to_dict(response)

@mutation.field('payInvoice')
async def r_pay_invoice(_, info, invoice, amt):
    assert not amt or amt >= 0
    if not (u := await info.context.user_from_header()):
        return {
            'ok': False,
            'error': 'Invalid auth token'
        }
    # obtain a db lock
    lock = Lock(
        info.context.redis,
        'invoice_paying_for' + u.userid
    )
    if not await lock.obtain_lock():
        info.context.logger.warning('Failed to acquire lock for user {}'.format(u.userid))
        return 'DB is locked try again later'
    user_balance = await u.get_calculated_balance()
    request = ln.PayReqString(pay_req=invoice)
    response = await make_async(info.context.lnd.DecodePayReq.future(request, timeout=5000))
    real_amount = response.num_satoshis if response.num_satoshis > 0 else amt
    info.context.logger.info(f'paying invoice user:{u.userid} with balance {user_balance}, for {real_amount}')
    if not real_amount:
        info.context.logger.warning(f'Invalid amount when paying invoice for user {u.userid}')
        return 'Invalid invoice amount'
    # check if user has enough balance including possible fees
    if not user_balance >= real_amount + floor(real_amount * 0.01):
        return 'Not enough balance to pay invoice'

    # determine destination of funds
    if info.context.id_pubkey == response.destination:
        # this is internal invoice now, receiver add balance
        userid_payee = await u.get_user_by_payment_hash(response.payment_hash)
        if not userid_payee:
            await lock.release_lock()
            info.context.logger.critical('Could not get user by payment hash')
            return 'Could not get user py payment hash'
        if await u.get_payment_hash_paid(response.payment_hash):
            # invoice has already been paid
            await lock.release_lock()
            info.context.logger.warning('Attempted to pay invoice that was already paid')
            return 'Invoice has already been paid'

        # initialize internal user payee
        payee = User(ctx=info.context)
        payee.userid = userid_payee # TODO fix me this is hackey
        await payee.clear_balance_cache()

        # sender spent his balance
        await u.clear_balance_cache()
        await u.save_paid_invoice({
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
        await u.lock_funds(invoice, response)
        for pay_res in info.context.lnd.SendPayment(req_gen()):
            # stream response synchronously FIXME
            await u.unlock_funds(invoice)
            if pay_res and pay_res.payment_route and pay_res.payment_route.total_amt_msat:
                # payment success
                shallow_paym = Paym(False, False, False) # weird FIXME
                payment = shallow_paym.process_send_payment_response(pay_res)
                payment.pay_req = invoice
                payment.decoded = response
                pay_dict = protobuf_to_dict(payment)
                await u.save_paid_invoice(pay_dict)
                await u.clear_balance_cache()
                await lock.release_lock()
                return payment
            else:
                # payment failed
                await lock.release_lock()
                return 'Payment Failed'
