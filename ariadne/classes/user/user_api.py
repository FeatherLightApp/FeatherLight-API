"""facade class for exposing methods on User GQL Object"""
from asyncio import iscoroutinefunction
from .abstract_user_method import AbstractMethod
from .btc_address import GetBTCAddress
from .invoices import GetUserInvoices
from .balance import GetBalance
from .onchain_txs import GetOnchainTxs
from .offchain_txs import GetOffchainTxs
from .lock_funds import LockFunds
from .unlock_funds import UnlockFunds
from helpers.mixins import LoggerMixin
from typing import Any

#TODO create a deafult resolver/ schema directive to abstract away need for this class

class User(LoggerMixin):
    #These are none unless expicitly set by a create function
    username = None
    password = None

    def __init__(self, userid, role):
        assert userid and role
        self.userid = userid
        self.role = role

    async def __call__(self, api_method: AbstractMethod) -> Any:
        if iscoroutinefunction(api_method.run):
            return await api_method.run(self)
        return api_method.run(self)


    def tokens(self, *_):
        # pass self to token resolver
        return self


    async def btc_address(self, *_):
        return await self(GetBTCAddress())

    async def balance(self, *_):
        return await self(GetBalance())


    async def invoices(self, *_, paid: bool = False, limit: int = 0):
        method = GetUserInvoices(only_paid=paid, limit=limit)
        return await self(method)


    async def payments(self, *_, start: int = 0, end: int = -1):
        method = GetOffchainTxs(start, end)
        return await self(method)


    async def deposits(self, *_):
        method = GetOnchainTxs(min_confirmations=3)
        return await self(method)


    async def lock_funds(self, *_, pay_req, invoice):
        method = LockFunds(pay_req, invoice)
        return await self(method)


    async def unlock_funds(self, *_, pay_req):
        method = UnlockFunds(pay_req)
        return await self(method)