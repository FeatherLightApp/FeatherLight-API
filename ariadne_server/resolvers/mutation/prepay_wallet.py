import os
from base64 import b64encode
from secrets import token_hex, token_bytes
from ariadne import MutationType
from pymacaroons import Macaroon
from context import LND
from models import LSAT
from classes import Error
import rpc_pb2 as ln


MUTATION = MutationType()

@MUTATION.field('prepayWallet')
async def r_prepay_wallet(*_, amount: int, memo: str):
    if amount < 10000:
        return Error('InsufficientFunds', 'Prepaid Wallets must have a value of at least 10000 sats')

    expiry_time = 3600*24
    preimage = token_bytes(32)
    macaroon_key = token_bytes(32)

    request = ln.Invoice(
        value=amount,
        memo=memo,
        expiry=expiry_time,
        r_preimage=preimage
    )

    inv = await LND.stub.AddInvoice(request)

    macaroon = Macaroon(
        location=os.environ.get('ENDPOINT'),
        identifier=b64encode(inv.r_hash).decode(),
        key=macaroon_key
    )

    # add macaroon caveats

    macaroon.add_first_party_caveat('uses = 1')
    macaroon.add_first_party_caveat('action = REDEEM_WALLET')
    # caveat is unecessary for validation and is only included so the token holder may know the amount being redeemed
    macaroon.add_first_party_caveat(f'amount = {amount}')

    lsat = await LSAT.create(
        key=macaroon_key,
        payment_hash=b64encode(inv.r_hash).decode(),
        preimage=b64encode(preimage).decode(),
        used=0,
        uses=1,
    )

    lsat.macaroon=macaroon.serialize()
    lsat.payment_request = inv.payment_request
    lsat.amount = amount

    return lsat




    
