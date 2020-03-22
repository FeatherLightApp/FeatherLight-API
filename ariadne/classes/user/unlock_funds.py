import json
from .abstract_user_method import AbstractMethod
from .locked_payments import GetLockedPayments
from context import REDIS

class UnlockFunds(AbstractMethod):

    def __init__(self, pay_req):
        self.pay_req = pay_req

    async def run(self, user):
        """
        Strips specific payreq from the list of locked payments
        """
        assert user.userid
        locked_payments_method = GetLockedPayments()
        payments = await user(locked_payments_method)
        save_back = []
        for paym in payments:
            if paym['pay_req'] != self.pay_req:
                save_back.append(paym)

        await REDIS.conn.delete('locked_payments_for_' + user.userid)
        for doc in save_back:
            await REDIS.conn.rpush('locked_payments_for_' + user.userid, json.dumps(doc))