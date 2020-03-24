"""
resolver for specific fields of invoice payload
remainder of field are resolved with the default resolvers
"""
from ariadne import InterfaceType
from context import LND
from helpers.async_future import make_async
import rpc_pb2 as ln

_invoice = InterfaceType('Invoice')

@_invoice.type_resolver
def r_invoice_type(obj, *_):
    if obj.get('value'):
        return 'PaidInvoice'
    return 'UserInvoice'


@_invoice.field('paymentPreimage')
async def resolve_preimage(obj, *_):
    if (preimage := obj.get('payment_preimage')):
        return preimage
    payment_hash = obj.get('payment_hash')
    #type cast the payment hash to bytes
    lookup_req = ln.PaymentHash(r_hash=payment_hash if isinstance(payment_hash, bytes) else bytes.fromhex(payment_hash))
    full_invoice = await make_async(LND.stub.LookupInvoice.future(lookup_req, timeout=5000))
    return full_invoice.r_preimage

INTERFACE = [
    _invoice
]
