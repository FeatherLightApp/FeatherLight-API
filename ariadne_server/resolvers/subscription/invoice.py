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


INVOICE = SubscriptionType()


@INVOICE.source('invoice')
async def r_invoice_gen(user: User, *_):
    #create new new pub sub client for streaming locally paid invoices
    local_stream = PUBSUB.add_client(user.username)

    #create stream for remotely paid invoices
    remote_stream = await LND.stub.SubscribeInvoices(ln.InvoiceSubscription())
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
                        updated = await invoice.update(
                            paid=True,
                            paid_at=invoice.settle_date
                        ).apply()
                        yield updated

            except GeneratorExit:
                # user closed stream, del pubsub queue
                del local_stream
                if len(PUBSUB[user.username]) == 0:
                    del PUBSUB[user.username]



@INVOICE.field('invoice')
def r_invoice_field(invoice, *_):
    return invoice
