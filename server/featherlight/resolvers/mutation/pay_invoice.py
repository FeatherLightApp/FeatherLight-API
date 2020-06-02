from typing import Optional
from base64 import b64encode, b16decode
from math import ceil
from time import time
from ariadne import MutationType
from grpclib.exceptions import GRPCError
from classes.user import User
from classes.error import Error
from models import Invoice, LSAT
from context import LND, GINO, PUBSUB
import rpc_pb2 as ln

MUTATION = MutationType()


# TODO split into multiple functions
@MUTATION.field("payInvoice")
async def r_pay_invoice(user: User, *_, invoice: str, amt: Optional[int] = None):
    # determine true invoice amount
    pay_string = ln.PayReqString(pay_req=invoice.replace("lightning:", ""))
    try:
        decoded = await LND.stub.DecodePayReq(pay_string)
    except GRPCError as e:
        return Error("PaymentError", str(e))

    if amt is not None and decoded.num_satoshis != amt and decoded.num_satoshis > 0:
        return Error("PaymentError", "Payment amount does not match invoice amount")

    if decoded.num_satoshis == 0 and not amt:
        return Error("PaymentError", "You must specify an amount for this tip invoice")

    payment_amt = amt or decoded.num_satoshis
    fee_limit = ceil(payment_amt * 0.01)

    # convert decoded hex to string b64
    b64_payment_hash = b64encode(
        b16decode(decoded.payment_hash, casefold=True)
    ).decode()

    # lock payer's db row before determining balance
    async with GINO.db.transaction():
        # potentially user.query.with_for..
        await user.query.with_for_update().gino.status()  # obtain lock
        user_balance = await user.balance()
        if payment_amt + fee_limit > user_balance:
            return Error(
                "InsufficientFunds",
                f"""Attempting to pay {payment_amt} sat
                with fee limit {fee_limit} sat
                with only {user_balance} sat""",
            )

        # determine if external node invoice
        if LND.id_pubkey != decoded.destination:

            req = ln.SendRequest(
                payment_request=invoice,
                amt=payment_amt,
                fee_limit=ln.FeeLimit(fixed=fee_limit),
            )

            invoice_obj = Invoice(
                payment_hash=b64_payment_hash,
                payment_request=invoice,
                timestamp=decoded.timestamp,
                expiry=decoded.expiry,
                memo=decoded.description,
                paid=False,  # not yet paid
                amount=decoded.num_satoshis,
                payer=user.username,
            )

            payment_res = await LND.stub.SendPaymentSync(req)
            if payment_res.payment_error or not payment_res.payment_preimage:
                return Error("PaymentError", payment_res.payment_error)

            invoice_obj.payment_preimage = b64encode(
                payment_res.payment_preimage
            ).decode()
            # impose maximum fee
            invoice_obj.fee = max(fee_limit, payment_res.payment_route.total_fees)
            invoice_obj.paid = True
            invoice_obj.paid_at = int(time())

            return await invoice_obj.create()

        # determine if internal user invoice
        elif LND.id_pubkey == decoded.destination and (
            invoice_obj := await Invoice.get(b64_payment_hash)
        ):
            if invoice_obj.paid:
                return Error("PaymentError", "This invoice has already been paid")
            # internal invoice, get payee from db
            if not (payee := await User.get(invoice_obj.payee)):
                # could not find the invoice payee in the db
                return Error("PaymentError", "This invoice is invalid")

            await invoice_obj.update(
                paid=True, payer=user.username, fee=fee_limit, paid_at=time()
            ).apply()

            # check if there are clients in the subscribe channel for this invoice
            if payee.username in PUBSUB.keys():
                # clients are listening, push to all open clients
                for client in PUBSUB[payee.username]:
                    await client.put(invoice_obj)

            return invoice_obj

        # determine if invoice corresponds to a node lsat
        elif LND.id_pubkey == decoded.destination and (
            lsat_obj := await LSAT.get(b64_payment_hash)
        ):

            return await Invoice.create(
                payment_hash=b64_payment_hash,
                payment_request=invoice,
                payment_preimage=lsat_obj.preimage,
                timestamp=decoded.timestamp,
                expiry=decoded.expiry,
                memo=decoded.description,
                paid=True,  # not yet paid
                amount=decoded.num_satoshis,
                payer=user.username,
                fee=fee_limit,
                paid_at=time(),
            )

        # unable to determine type of invoice
        else:
            return Error("PaymentError", "This invoice is invalid")
