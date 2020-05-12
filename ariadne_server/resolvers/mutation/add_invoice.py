from typing import Optional, Union
from base64 import b64encode as encode64

from ariadne import MutationType

from classes.user import User
from classes.error import Error
from models import Invoice
from context import LND
import rpc_pb2 as ln

MUTATION = MutationType()

@MUTATION.field('addInvoice')
# TODO add more flexiblilty in invoice creation
async def r_add_invoice(
    user: User,
    *_,
    memo: str,
    amt: int,
    set_hash: Optional[bytes] = None
) -> Union[Invoice, Error]:

    if amt <= 0:
        return Error('InvalidInvoice', f'Invalid amount: {amt}')
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
        payment_hash=encode64(inv.r_hash).decode(),
        payment_request=inv.payment_request,
        payment_preimage=encode64(inv_lookup.r_preimage).decode(),
        timestamp=inv_lookup.creation_date,
        expiry=inv_lookup.expiry,
        memo=inv_lookup.memo,
        paid=False,
        amount=inv_lookup.value,
        # do not set a fee since this invoice has not been paid
        payee=user.username
        # do not set a payer since we dont know to whom to invoice is being sent
    )