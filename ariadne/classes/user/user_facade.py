"""facade class for exposing methods on User GQL Object"""
from .base_user import Base_User
from .btc_address import GetBTCAddress
from .invoices import GetUserInvoices
from .balance import GetBalance
from .onchain_txs import GetOnchainTxs
from .offchain_txs import GetOffchainTxs
from .lock_funds import LockFunds
from .unlock_funds import UnlockFunds
from helpers.mixins import LoggerMixin

#TODO create a deafult resolver/ schema directive to abstract away need for this class

class User(LoggerMixin):
    #These are none unless expicitly set by a create function
    username = None
    password = None

    def __init__(self, userid):
        super().__init__()
        self.userid = userid
        self._base_user = Base_User(userid)


    async def btc_address(self, info):
        method = GetBTCAddress()
        return await self._base_user.execute(method)

    async def balance(self, info):
        method = GetBalance()
        return await self._base_user.execute(method)


    async def invoices(self, info, *, paid: bool = False, start: int = 0, end: int = -1):
        method = GetUserInvoices(only_paid = paid, start = start, end = end)
        return await self._base_user.execute(method)


    async def payments(self, info, start: int = 0, end: int = -1):
        method = GetOffchainTxs()
        return await self._base_user.execute(method)


    async def deposits(self, info):
        method = GetOnchainTxs(min_confirmations=3)
        return await self._base_user.execute(method)


    async def lock_funds(self, info, pay_req, invoice):
        method = LockFunds(pay_req, invoice)
        return await self._base_user.execute(method)


    async def unlock_funds(self, info, pay_req):
        method = UnlockFunds(pay_req)
        return await self._base_user.execute(method)
