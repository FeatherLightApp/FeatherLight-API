"""facade class for exposing methods on User GQL Object"""
from .base_user import Base_User
from .btc_address import GetBTCAddress
from .invoices import GetUserInvoices
from .balance import GetBalance
from .onchain_txs import GetOnchainTxs
from code.helpers.mixins import LoggerMixin

#TODO create a deafult resolver/ schema directive to abstract away need for this class

class User(LoggerMixin):
    #These are none unless expicitly set by a create function
    username = None
    password = None

    def __init__(self, userid):
        super().__init__()
        self.userid = userid

    def _get_gateway(self, ctx):
        return Base_User(self.userid, ctx)

    async def btc_address(self, info):
        method = GetBTCAddress()
        user = self._get_gateway(info.context)
        return await user.execute(method)

    async def balance(self, info):
        method = GetBalance()
        user = self._get_gateway(info.context)
        return await user.execute(method)


    async def invoices(self, info, *, paid: bool = False, start: int = 0, end: int = -1):
        method = GetUserInvoices(only_paid = paid, start = start, end = end)
        user = self._get_gateway(info.context)
        return await user.execute(method)


    async def deposits(self, info):
        method = GetOnchainTxs(min_confirmations=3)
        user = self._get_gateway(info.context)
        return await user.execute(method)

