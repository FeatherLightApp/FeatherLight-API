"""module for getting user invoices"""
from helpers.async_future import make_async
from context import LND, GINO
from models import Invoice as DB_Invoice
import rpc_pb2 as ln
from .abstract_user_method import AbstractMethod


class GetUserInvoices(AbstractMethod):
    """Method for retriving a user's invoices, either paid or unpaid"""

    def __init__(self, only_paid: bool = True, limit: int = 0, offset: int = 0):
        self._only_paid = only_paid
        self._limit = limit
        self._offset = offset

    async def run(self, user):
        """
        retrives invoices (payment requests) for current user from redis and returns
        them with payment state based on gRPC query.
        Side Effect: adds true lnd invoices as paid in redis
        Internal invoices are marked as paid on payment send
        """

        invoices = []
        async with GINO.db.transaction():
            async for invoice in DB_Invoice.query \
                .where(DB_Invoice.payee == user.id) \
                .limit(self._limit) \
                .offset(self._offset) \
                    .gino.iterate():

                if not invoice.paid:
                    # if not paid check lnd to see if its paid in lnd db
                    # convert hex serialized payment hash to bytes

                    req = ln.PaymentHash(
                        r_hash=bytes.fromhex(invoice.payment_hash))
                    lookup_info = await make_async(LND.stub.LookupInvoice.future(req, timeout=5000))

                    if lookup_info.state == 1:
                        # invoice is paid update state in db
                        await invoice.update(paid=True).apply()

                invoices.append(invoice)
        # if only paid is false return all results else return only settled ammounts
        return [invoice for invoice in invoices if not self._only_paid or invoice.paid]
