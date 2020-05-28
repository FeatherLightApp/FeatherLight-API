from base64 import b64decode
from secrets import token_bytes, token_hex
from time import time
from ariadne import MutationType
from pymacaroons import Macaroon
from models import LSAT, Invoice
from classes import User
from context import ARGON, LND
import rpc_pb2 as ln


MUTATION = MutationType()

@MUTATION.field('redeemWallet')
async def r_redeem_wallet(data: LSAT, info):

    password = token_hex(10)
    # save to db
    user = await User.create(
        key=token_bytes(32),
        username=token_hex(10),
        password_hash=ARGON.hash(password),
        role='USER',
        created=time()
    )

    # decode b64 to bytes
    pay_hash = ln.PaymentHash(r_hash=b64decode(lsat.payment_hash.encode('utf-8')))
    inv_lookup = await LND.stub.LookupInvoice(pay_hash)

    invoice = await Invoice.create(
        payment_hash=lsat.payment_hash,
        payment_preimage=lsat.preimage,
        payment_request=inv_lookup.payment_request,
        timestamp=inv_lookup.creation_date,
        expiry=inv_lookup.expiry,
        memo=inv_lookup.memo,
        paid=True,
        amount=inv_lookup.value,
        payee=user.username
    )

    lsat_used = lsat.used + 1
    if lsat_used == lsat.uses:
        # lsat has been used up
        lsat.delete()
    else:
        lsat.update(used=lsat_used)
    
    return user



