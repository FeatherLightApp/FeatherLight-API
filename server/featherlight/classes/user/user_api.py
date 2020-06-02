"""facade class for exposing methods on User GQL Object and subclassing the gino model"""
from asyncio import iscoroutinefunction
from typing import Any
from helpers.mixins import LoggerMixin
from models import User as UserModel
from .abstract_user_method import AbstractMethod
from .btc_address import GetBTCAddress
from .invoices import GetInvoices
from .balance import GetBalance
from .onchain_txs import GetOnchainTxs
from models.invoice import Invoice

# TODO create a deafult resolver/ schema directive to abstract away need for this class


class User(LoggerMixin, UserModel):
    # These are none unless expicitly set by a create function
    password = None

    async def exec(self, api_method: AbstractMethod) -> Any:
        if iscoroutinefunction(api_method.run):
            return await api_method.run(self)
        return api_method.run(self)

    def tokens(self, *_):
        # pass self to token resolver
        return self

    async def feed(
        self,
        *_,
        limit: int,
        paid: bool,
        expired: bool = True,
        confirmations: int = 3,
        offset: int = 0
    ):
        inv = await self.exec(GetInvoices(paid=paid, limit=limit, expired=expired))
        dep = await self.exec(
            GetOnchainTxs(min_confirmations=confirmations, limit=limit)
        )

        def get_time(x) -> int:
            if isinstance(x, Invoice):
                if x.payee == self.username:
                    return x.timestamp
                if x.payer == self.username:
                    return x.paid_at
            return x["time"]

        return sorted([*inv, *dep], key=get_time, reverse=True)[offset : offset + limit]

    async def btc_address(self, *_):
        """returns btc address if its stored in db else generate btc address"""
        if self.bitcoin_address:
            return self.bitcoin_address
        return await self.exec(GetBTCAddress())

    async def balance(self, *_):
        return await self.exec(GetBalance())

    async def invoices(
        self, *_, paid: bool, limit: int, offset: int = 0, expired: bool = False
    ):
        method = GetInvoices(
            paid=paid,
            limit=limit,
            offset=offset,
            expired=expired,
            payee=True,
            payer=False,
        )
        return await self.exec(method)

    async def payments(self, *_, limit: int, offset: int = 0):
        method = GetInvoices(
            paid=True, limit=limit, offset=offset, payee=False, payer=True
        )
        return await self.exec(method)

    async def deposits(self, *_, confirmations: int):
        method = GetOnchainTxs(min_confirmations=confirmations)
        return await self.exec(method)

    # TODO determine if deprecated
    # async def lock_funds(self, *_, pay_req, invoice):
    #     method = LockFunds(pay_req, invoice)
    #     return await self.exec(method)

    # TODO determine of deprecated
    # async def unlock_funds(self, *_, pay_req):
    #     method = UnlockFunds(pay_req)
    #     return await self.exec(method)
