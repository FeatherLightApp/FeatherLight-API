import json
from .abstract_user_method import AbstractMethod

class GetLockedPayments(AbstractMethod):

    def __init__(self, start: int = 0, end: int = -1):
        self.start = start
        self.end = end

    async def run(self, user):
        """
        retrives the locked payments for a user
        locked payments are outbound transactions that have not yet been accepted
        this is used to calculate a users balance correctly before tranctaions has been settled
        """
        payments = await user.ctx.redis.lrange('locked_payments_for_' + user.userid, self.start, self.end)
        result = []
        for paym in payments:
            try:
                data = json.loads(paym.decode('utf-8'))
                result.append(data)
            except json.decoder.JSONDecodeError as error:
                self.logger.critical(error)
        return result