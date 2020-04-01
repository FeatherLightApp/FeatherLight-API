from time import time
from math import floor
from secrets import token_hex
from typing import Union, Optional
from ariadne import MutationType
from argon2.exceptions import VerificationError
from classes.user import User
from classes.error import Error
from helpers.mixins import LoggerMixin
from helpers.crypto import decode
from context import LND, ARGON, GINO, PUBSUB
from models import Invoice
import rpc_pb2 as ln

MUTATION = MutationType()

_mutation_logger = LoggerMixin()


@MUTATION.field('createUser')
# TODO add post limiter?
async def r_create_user(*_, role: str = 'USER') -> User:
    """create a new user and save to db"""
    # create api object
    password = token_hex(10)
    # save to db
    user = await User.create(
        id=token_hex(10),
        username=token_hex(10),
        password_hash=ARGON.hash(password),
        role=role,
        created=time()
    )
    #set password field on user to pass them their password 1 time
    user.password = password
    # return api object to resolver
    return user


@MUTATION.field('login')
async def r_auth(*_, username: str, password: str) -> Union[User, Error]:
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


# TODO GET RID OF THIS ITS FOR DEBUG
@MUTATION.field('forceUser')
async def r_force_user(*_, user: str) -> str:
    if not (user_obj:= await User.get(user)):
        return Error('AuthenticationError', 'User not found in DB')
    return user_obj


@MUTATION.field('refreshAccessToken')
async def r_get_token(_: None, info) -> Union[User, Error]:
    # catch scenario of no refresh cookie
    if not (cookie:= info.context['request'].cookies.get('refresh')):
        return Error(error_type='AuthenticationError', message='No refresh token sent')
    decode_response: Union[dict, Error] = decode(token=cookie, kind='refresh')
    # pass either error or user instance to union resolver
    _mutation_logger.logger.critical(decode_response)
    if isinstance(decode_response, Error):
        return decode_response
    if isinstance(decode_response, dict):
        # lookup userid from db and return
        return await User.get(decode_response['id'])


@MUTATION.field('addInvoice')
# TODO add more flexiblilty in invoice creation
# TODO invoiceFor allows creating invoices for other users on their behalf
# FIXME doesnt work
async def r_add_invoice(user: User, *_, memo: str, amt: int, invoiceFor: Optional[str] = None) -> dict:
    """Authenticated route"""
    expiry_time = 3600*24
    request = ln.Invoice(
        memo=memo,
        value_msat=amt,
        expiry=expiry_time
    )
    inv = await LND.stub.AddInvoice(request)

    # lookup invoice to get preimage
    pay_hash = ln.PaymentHash(r_hash=inv.r_hash)
    inv_lookup = await LND.stub.LookupInvoice(pay_hash)
    
    return await Invoice.create(
        payment_hash=inv.r_hash.hex(),
        payment_request=inv.payment_request,
        payment_preimage=inv_lookup.r_preimage.hex(),
        timestamp=inv_lookup.creation_date,
        expiry=inv_lookup.expiry,
        memo=inv_lookup.memo,
        paid=False,
        msat_amount=inv_lookup.value_msat,
        # do not set a fee since this invoice has not been paid
        payee=user.id
        # do not set a payer since we dont know to whom to invoice is being sent
    )


@MUTATION.field('payInvoice')
async def r_pay_invoice(user: User, *_, invoice: str, amt: Optional[int] = None):
    #determine true invoice amount
    pay_string = ln.PayReqString(pay_req=invoice)
    decoded = await LND.stub.DecodePayReq(pay_string)

    if amt is not None and decoded.num_msat != amt and decoded.num_msat > 0:
        return Error('PaymentError', 'Payment amount does not match invoice amount')

    if decoded.num_msat == 0 and not amt:
        return Error('PaymentError', 'You must specify an amount for this tip invoice')

    payment_amt = amt or decoded.num_msat

    # attempt to load invoice obj
    invoice_obj = await Invoice.get(decoded.payment_hash)
    if invoice_obj and invoice_obj.paid:
        return Error('PaymentError', 'This invoice has already been paid')

    #lock payer's db row before determining balance
    async with GINO.db.transaction():
        # potentially user.query.with_for..
        user.query.with_for_update().gino.status() #obtain lock
        user_balance = await user.balance()
        if payment_amt > await user_balance:
            return Error(
                'InsufficientFunds',
                f'Attempting to pay {payment_amt} with only {user_balance}'
            )
  
        if LND.id_pubkey == decoded.payment_hash and invoice_obj:
            #internal invoice, get payee from db
            if not (payee := await User.get(invoice_obj.payee)):
                # could not find the invoice payee in the db
                return Error('PaymentError', 'This invoice is invalid')

            invoice_update = invoice_obj.update(
                paid=True,
                payer=user.id,
                msat_fee=floor(payment_amt * 0.03),
                paid_at=time()
            )

            # check if there are clients in the subscribe channel for this invoice
            if payee.id in PUBSUB.keys():
                # clients are listening, push to all open clients
                for client in PUBSUB[payee.id]:
                    await client.put(invoice_update)

            #send update coroutine to background task
            await PUBSUB.background_tasks.put(invoice_update.apply)

            return invoice_update
        
        # proceed with external payment if invoice does not exist in db already
        elif not invoice_obj:
            fee_limit = floor(payment_amt * 0.005) + 1000 #add 1 satoshi

            def req_gen():
                yield ln.SendRequest(
                    payment_request=invoice,
                    amt_msat=payment_amt,
                    fee_limit=ln.FeeLimit(fixed=fee_limit)
                )

            invoice_obj = Invoice(
                payment_hash=decoded.payment_hash,
                payment_request=invoice,
                timestamp=decoded.timestamp,
                expiry=decoded.expiry,
                memo=decoded.description,
                paid=False, # not yet paid
                msat_amount=decoded.num_msat or decoded.num_satoshis * 1000,
                payer=user.id
            )

            # TODO find native async way to execute
            for payment_res in LND.stub.SendPayment(req_gen()):
                _mutation_logger.logger.info(f"payment response: {payment_res}")
                if payment_res.payment_error or not payment_res.payment_preimage:
                    return Error('PaymentError', f"received error {payment_res.payment_error}")

                invoice_obj.payment_preimage = payment_res.payment_preimage.hex()
                invoice_obj.msat_fee = max(fee_limit, payment_res.payment_route.total_fees)
                invoice_obj.paid = True
                invoice_obj.paid_at = time()
                invoice_obj.create()
                return invoice_obj
