"""File to define method for retriving offchain txs"""
import json
from .abstract_user_method import AbstractMethod
from ...helpers.mixins import LoggerMixin
from ...context import REDIS

class GetOffchainTxs(AbstractMethod, LoggerMixin):
    """Method for retrieving offchain txs of a user"""

    def __init__(self, start: int = 0, end: int = -1):
        # requesting end of 0 returns last tx
        self.start = start
        self.end = end


    async def run(self, user):
        """
        Return offchain invoices that were paid by this user and stored in redis via save_paid_invoice
        """
        result = []
        ranges = await REDIS.conn.lrange(f"paid_invoices_for_{user.userid}", self.start, self.end)
        #item is a byte encoded json representation of processSendPaymentResponse
        for item in ranges:
            invoice = json.loads(item.decode('utf-8'))

            invoice['paid'] = True
            invoice.pop('payment_error', None)
            invoice.pop('payment_route', None)
            result.append(invoice)

        self.logger.info(result)
        return result