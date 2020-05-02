"""module for getting user invoices"""
import base64
from context import LND, GINO
from models import Invoice as DB_Invoice
import rpc_pb2 as ln
from .abstract_user_method import AbstractMethod
from helpers.mixins import LoggerMixin


class GetInvoices(AbstractMethod, LoggerMixin):
    """Method for retriving a user's invoices, either paid or unpaid"""

    def __init__(
        self,
        only_paid: bool = True,
        limit: int = 0,
        offset: int = 0,
        payee: bool = True, 
        payer: bool = True
    ):
        self._only_paid = only_paid
        self._limit = limit
        self._offset = offset
        self._query = lambda x, y: (x.payee == y if payee else False) or (x.payer == y if payer else False)

    async def run(self, user):
        """
        retrives invoices (payment requests) for current user and returns
        them with payment state based on gRPC query.
        Side Effect: adds true lnd invoices as paid in redis
        Internal invoices are marked as paid on payment send
        """

        invoices = []
        async with GINO.db.transaction():
            async for invoice in DB_Invoice.query \
                .where(self._query(DB_Invoice, user.username)) \
                .limit(self._limit) \
                .offset(self._offset) \
                .gino.iterate():
                    self.logger.critical(invoice)
                    if not invoice.paid:
                        # if not paid check lnd to see if its paid in lnd db

                        req = ln.PaymentHash(
                            r_hash=base64.b64decode(invoice.payment_hash.encode('utf-8'))
                        )
                        lookup_info = await LND.stub.LookupInvoice(req)

                        if lookup_info.state == 1:
                            # invoice is paid update state in db
                            await invoice.update(
                                paid=True,
                                paid_at=lookup_info.settle_date
                            ).apply()

                    invoices.append(invoice)
        # if only paid is false return all results else return only settled ammounts
        return [invoice for invoice in invoices if not self._only_paid or invoice.paid]
