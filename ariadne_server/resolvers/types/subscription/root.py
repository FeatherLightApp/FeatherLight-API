import asyncio
from typing import Union
from ariadne import SubscriptionType, UnionType
from aiostream import stream
import rpc_pb2 as ln
from context import LND, PUBSUB
from models import Invoice
from classes.user import User
from classes.error import Error
from helpers.mixins import LoggerMixin

_sub_logger = LoggerMixin()


_SUBSCRIPTION = SubscriptionType()


@_SUBSCRIPTION.source('invoice')
async def r_invoice_gen(user: User, *_):
    _sub_logger.logger.critical('entering generator with root: %s', user)
    #create new new pub sub client for streaming locally paid invoices
    local_stream = PUBSUB.add_client(user.username)

    #create stream for remotely paid invoices
    remote_stream = await LND.stub.SubscribeInvoices(ln.InvoiceSubscription())
    _sub_logger.logger.critical(type(local_stream))
    _sub_logger.logger.critical(type(remote_stream))
    global_stream = stream.merge(local_stream, remote_stream)

    async with global_stream.stream() as streamer:
        async for response in streamer:
            try:
                # check if response if from lnd - external payment or pubsub - local payment
                if isinstance(response, Invoice):
                    # invoice model received from pubsub client
                    # yield this and default resolver will retrieve requested fields
                    yield response
                else:
                    # payment comes from lnd, check if its associated with this user
                    invoice = None
                    if response.state == 1:
                        invoice = await Invoice.get(response.r_hash)
                    if invoice and invoice.payee == user.username:
                        #received a paid invoice with this user as payee
                        updated = invoice.update(
                            paid=True,
                            paid_at=invoice.settle_date
                        )
                        yield updated
                        # delegate db write to background process
                        loop = asyncio.get_running_loop()
                        loop.create_task(updated.apply())
            except GeneratorExit:
                # user closed stream, del pubsub queue
                del local_stream
                if len(PUBSUB[user.username]) == 0:
                    del PUBSUB[user.username]



@_SUBSCRIPTION.field('invoice')
def r_invoice_field(invoice, *_):
    _sub_logger.logger.critical('sub field %s', invoice)
    return invoice


_PAID_INVOICE_RESPONSE = UnionType('PaidInvoiceResponse')

@_PAID_INVOICE_RESPONSE.type_resolver
def r_paid_invoice_response(obj, *_):
    _sub_logger.logger.critical('union logger %s', obj)
    if isinstance(obj, Error):
        return 'Error'
    return 'UserInvoice'


EXPORT = [
    _PAID_INVOICE_RESPONSE,
    _SUBSCRIPTION
]
