"""module for getting balance of user"""
import math
from .abstract_user_method import AbstractMethod
from .invoices import GetUserInvoices
from .onchain_txs import GetOnchainTxs
from .offchain_txs import GetOffchainTxs
from .locked_payments import GetLockedPayments
from ...helpers.mixins import LoggerMixin

class GetBalance(AbstractMethod, LoggerMixin):
    """method to get the calculated balance for the user"""

    async def run(self, user):
        balance = 0

        #asking for 0 invoices returns all invoices
        invoice_method = GetUserInvoices(only_paid=True)
        for paid_invoice in await user(invoice_method):
            balance += paid_invoice['amount']

        onchain_txfer_method = GetOnchainTxs(min_confirmations=3)
        for transaction in await user(onchain_txfer_method):
            # Valid onchain btc transactions sent to this user's address
            # Debit user's account balance
            balance += transaction['amount']

        offchain_txfer_method = GetOffchainTxs()
        for invoice in await user(offchain_txfer_method):
            # for each dict in list of invoices paid by this user
            # Credit user's account balance for full value including fees
            balance -= invoice['value']

        locked_payments_method = GetLockedPayments()
        for invoice in await user(locked_payments_method):
            # for each locked payment (invoice that has been sent but not validated)
            # Credit user's account balance
            balance -= invoice['amount'] + math.floor(invoice['amount'] * 0.01) #fee limit

        return balance