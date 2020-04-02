"""
resolver for specific fields of invoice payload
remainder of field are resolved with the default resolvers
"""
from ariadne import InterfaceType
from context import LND
import rpc_pb2 as ln

_invoice = InterfaceType('Invoice')


@_invoice.type_resolver
def r_invoice_type(obj, *_):
    if obj.get('value'):
        return 'PaidInvoice'
    return 'UserInvoice'

INTERFACE = [
    _invoice
]
