import json
from datetime import datetime
from .abstract_user_method import AbstractMethod
from ...context import REDIS

class LockFunds(AbstractMethod):

    def __init__(self, pay_req, invoice):
        self.invoice = invoice
        self.pay_req = pay_req


    async def run(self, user):
        """
        Adds invoice to a list of user's locked payments.
        Used to calculate balance till the lock is lifted
        (payment is in determined state - success or fail)
        """
        assert user.userid
        utc_seconds = (datetime.utcnow() - datetime(1970, 1, 1)).total_seconds()
        doc = {
            'pay_req': self.pay_req,
            'amount': self.invoice.num_satoshis,
            'timestamp': utc_seconds
        }
        return REDIS.conn.rpush('locked_payments_for_' + user.userid, json.dumps(doc))

