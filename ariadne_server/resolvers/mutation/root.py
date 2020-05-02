import asyncio
from time import time
from math import floor, ceil
from secrets import token_hex, token_bytes
from typing import Union, Optional
import base64

from ariadne import MutationType
from argon2.exceptions import VerificationError
from grpclib.exceptions import GRPCError

from classes.user import User
from classes.error import Error
from helpers.mixins import LoggerMixin
from helpers.crypto import verify
from context import LND, ARGON, GINO, PUBSUB
from models import Invoice
import rpc_pb2 as ln

_MUTATION = MutationType()

_mutation_logger = LoggerMixin()


@_MUTATION.field('createUser')
# TODO add post limiter?
async def r_create_user(*_, role: str = 'USER') -> User:
    """create a new user and save to db"""
    # create api object
    password = token_hex(10)
    # save to db
    user = await User.create(
        key=token_bytes(32),
        username=token_hex(10),
        password_hash=ARGON.hash(password),
        role=role,
        created=time()
    )
    #set password field on user to pass them their password 1 time
    user.password = password
    # return api object to resolver
    return user

# this function is redundant as auth directive knows to send user obj
# to downstream union resolver. Function can intercept user and add functionality
@_MUTATION.field('refreshMacaroons')
def r_refresh_macaroons(user: User, info) -> User:
    _mutation_logger.logger.critical('refreshing token')
    _mutation_logger.logger.critical(info.context['request'].headers)
    #pass user into token payload resolver
    return user


@_MUTATION.field('login')
async def r_login(*_, username: str, password: str) -> Union[User, Error]:
    if not (user_obj := await User.query.where(User.username == username).gino.first()):
        return Error('AuthenticationError', 'User not found')
    # verify pw hash
    try:
        ARGON.verify(user_obj.password_hash, password)
    except VerificationError:
        return Error('AuthenticationError', 'Incorrect password')

    if ARGON.check_needs_rehash(user_obj.password_hash):
        await user_obj.update(password_hash=ARGON.hash(password)).apply()

    return user_obj


@_MUTATION.field('logout')
async def r_logout (user: User, *_) -> None:
    await user.update(key=token_bytes(32)).apply()
    return None


# TODO GET RID OF THIS ITS FOR DEBUG
@_MUTATION.field('forceUser')
async def r_force_user(*_, user: str) -> str:
    if not (user_obj:= await User.get(user)):
        return Error('AuthenticationError', 'User not found in DB')
    return user_obj


@_MUTATION.field('addInvoice')
# TODO add more flexiblilty in invoice creation
async def r_add_invoice(
    user: User,
    *_,
    memo: str,
    amt: int,
    set_hash: Optional[bytes] = None
) -> Invoice:
    """Authenticated route"""
    expiry_time = 3600*24
    request = ln.Invoice(
        memo=memo,
        value=amt,
        expiry=expiry_time,
        r_hash=set_hash
    )
    inv = await LND.stub.AddInvoice(request)

    # lookup invoice to get preimage
    pay_hash = ln.PaymentHash(r_hash=inv.r_hash)
    inv_lookup = await LND.stub.LookupInvoice(pay_hash)
    
    return await Invoice.create(
        payment_hash=base64.b64encode(inv.r_hash).decode('utf-8'),
        payment_request=base64.b64encode(inv.payment_request).decode('utf-8'),
        payment_preimage=inv_lookup.r_preimage,
        timestamp=inv_lookup.creation_date,
        expiry=inv_lookup.expiry,
        memo=inv_lookup.memo,
        paid=False,
        amount=inv_lookup.value,
        # do not set a fee since this invoice has not been paid
        payee=user.username
        # do not set a payer since we dont know to whom to invoice is being sent
    )


@_MUTATION.field('payInvoice')
async def r_pay_invoice(user: User, *_, invoice: str, amt: Optional[int] = None):
    #determine true invoice amount
    pay_string = ln.PayReqString(pay_req=invoice.replace('lightning:', ''))
    try:
        decoded = await LND.stub.DecodePayReq(pay_string)
    except GRPCError as e:
        return Error('PaymentError', e)

    if amt is not None and decoded.num_satoshis != amt and decoded.num_satoshis > 0:
        return Error('PaymentError', 'Payment amount does not match invoice amount')

    if decoded.num_satoshis == 0 and not amt:
        return Error('PaymentError', 'You must specify an amount for this tip invoice')

    payment_amt = amt or decoded.num_satoshis
    fee_limit = ceil(payment_amt * 0.01)

    # attempt to load invoice obj
    invoice_obj = await Invoice.get(decoded.payment_hash)
    if invoice_obj and invoice_obj.paid:
        return Error('PaymentError', 'This invoice has already been paid')

    #lock payer's db row before determining balance
    async with GINO.db.transaction():
        # potentially user.query.with_for..
        user.query.with_for_update().gino.status() #obtain lock
        user_balance = await user.balance()
        if payment_amt + fee_limit > user_balance:
            return Error(
                'InsufficientFunds',
                f'''Attempting to pay {payment_amt} sat
                with fee limit {fee_limit} sat
                with only {user_balance} sat'''
            )

        if LND.id_pubkey == decoded.payment_hash and invoice_obj:
            #internal invoice, get payee from db
            if not (payee := await User.get(invoice_obj.payee)):
                # could not find the invoice payee in the db
                return Error('PaymentError', 'This invoice is invalid')

            invoice_update = invoice_obj.update(
                paid=True,
                payer=user.username,
                fee=fee_limit,
                paid_at=time()
            )

            # check if there are clients in the subscribe channel for this invoice
            if payee.username in PUBSUB.keys():
                # clients are listening, push to all open clients
                for client in PUBSUB[payee.username]:
                    await client.put(invoice_update)

            #send update coroutine to background task
            loop = asyncio.get_running_loop()
            loop.create_task(invoice_update.apply())

            return invoice_update
        
        # proceed with external payment if invoice does not exist in db already
        elif not invoice_obj:

            req = ln.SendRequest(
                    payment_request=invoice,
                    amt=payment_amt,
                    fee_limit=ln.FeeLimit(fixed=fee_limit)
            )

            invoice_obj = Invoice(
                payment_hash=decoded.payment_hash,
                payment_request=invoice,
                timestamp=decoded.timestamp,
                expiry=decoded.expiry,
                memo=decoded.description,
                paid=False, # not yet paid
                amount=decoded.num_satoshis,
                payer=user.username
            )

            payment_res = await LND.stub.SendPaymentSync(req)
            _mutation_logger.logger.info("payment response: %s", payment_res)
            if payment_res.payment_error or not payment_res.payment_preimage:
                return Error('PaymentError', f"received error {payment_res.payment_error}")

            invoice_obj.payment_preimage = payment_res.payment_preimage
            # impose maximum fee
            invoice_obj.fee = max(fee_limit, payment_res.payment_route.total_fees)
            invoice_obj.paid = True
            invoice_obj.paid_at = time()
            # delegate db write to background task
            loop = asyncio.get_running_loop()
            loop.create_task(invoice_obj.create())

            return invoice_obj
