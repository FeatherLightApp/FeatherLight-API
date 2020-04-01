from typing import Union
from ariadne import SubscriptionType, UnionType
import rpc_pb2 as ln
from context import LND
from models import Invoice
from classes.user import User
from classes.error import Error


_SUBSCRIPTION = SubscriptionType()


@_SUBSCRIPTION.source('invoice')
async def r_invoice_gen(user: Union[User, Error], *_):
    if isinstance(user, Error):
        # user wasnt authenticated from schema directive
        # pass error to union resolver and close generator
        yield user
        return

    req = ln.InvoiceSubscription()
    async for invoice in LND.stub.SubscribeInvoices(req):
        invoice_obj = None
        if invoice.state == 1:
            invoice_obj = await Invoice.get(invoice.r_hash.hex())
        if invoice_obj and invoice_obj.payee == user.id:
            updated_invoice = invoice_obj.update(
                paid=True,
                paid_at=invoice.settle_date
            )
            yield updated_invoice
            # mark new invoice as paid in db
            await updated_invoice.apply()


@_SUBSCRIPTION.field('invoice')
def r_invoice_field(invoice, *_):
    return invoice


_PAID_INVOICE_RESPONSE = UnionType('PaidInvoiceResponse')

@_PAID_INVOICE_RESPONSE.type_resolver
def r_paid_invoice_response(obj, *_):
    if isinstance(obj, Error):
        return 'Error'
    return 'UserInvoice'


EXPORT = [
    _PAID_INVOICE_RESPONSE,
    _SUBSCRIPTION
]