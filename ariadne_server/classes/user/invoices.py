"""module for getting user invoices"""
from time import time
from base64 import b64decode as decode64
from sqlalchemy import or_, and_
from context import LND, GINO
from models import Invoice as DB_Invoice
import rpc_pb2 as ln
from .abstract_user_method import AbstractMethod
from helpers.mixins import LoggerMixin


class GetInvoices(AbstractMethod, LoggerMixin):
    """Method for retriving a user's invoices, either paid or unpaid"""

    def __init__(
        self,
        paid: bool = True, #limit responses to only paid invoices
        limit: int = 0, #limit number of responses
        offset: int = 0, #offset index of search
        expired: bool = False, #include unpaid expired invoices
        payee: bool = True, #return invoices where current user is implicated as payee
        payer: bool = True #return invoices where current user is implcated as payer
    ):
        self._limit = limit
        self._offset = offset
        self._payee = payee
        self._payer = payer
        self._filter = lambda x: x.paid or expired or (x.timestamp + x.expiry < time()) and (x.paid or not paid)

    async def run(self, user):
        """
        retrives invoices (payment requests) for current user and returns
        them with payment state based on gRPC query.
        Side Effect: adds true lnd invoices as paid in redis
        Internal invoices are marked as paid on payment send
        """
        statement = DB_Invoice.query.where(or_(
            and_(DB_Invoice.payee == user.username, self._payee),
            and_(DB_Invoice.payer == user.username, self._payer)
        ))
        if self._limit > 0:
            statement = statement.limit(self._limit)
        statement = statement.offset(self._offset)
        invoices = []
        async with GINO.db.transaction():
            async for invoice in statement.gino.iterate():
                if not invoice.paid:
                    # if not paid check lnd to see if its paid in lnd db

                    req = ln.PaymentHash(
                        r_hash=decode64(invoice.payment_hash.encode('utf-8'))
                    )
                    lookup_info = await LND.stub.LookupInvoice(req)

                    if lookup_info.state == 1:
                        # invoice is paid update state in db
                        await invoice.update(
                            paid=True,
                            paid_at=lookup_info.settle_date
                        ).apply()

                if self._filter(invoice):
                    invoices.append(invoice)
        # TODO convert to asynchronous generator?
        return invoices
