import json
from time import time
from .abstract_user_method import AbstractMethod
from context import REDIS

#TODO determine if should be switched in to sql db
#TODO determine if this file is deprecated with use of postgres lock

class LockFunds(AbstractMethod):

    def __init__(self, pay_req, invoice):
        self.invoice = invoice
        self.pay_req = pay_req

    async def run(self, user):
        """
        Adds invoice to a list of user's locked payments.
        Used to calculate balance till the lock is lifted
        (payment is in determined state - success or fail)
        This only applied to external payments, internal ones are atomic
        """
        assert user.username
        doc = {
            'pay_req': self.pay_req,
            'amount': self.invoice.num_satoshis,
            'timestamp': time()
        }
        return REDIS.conn.rpush('locked_payments_for_' + user.username, json.dumps(doc))
