"""module for getting balance of user"""
import math
from helpers.mixins import LoggerMixin
from .abstract_user_method import AbstractMethod
from .invoices import GetInvoices
from .onchain_txs import GetOnchainTxs
from .offchain_txs import GetOffchainTxs
from .locked_payments import GetLockedPayments


class GetBalance(AbstractMethod, LoggerMixin):
    """method to get the calculated balance for the user"""

    async def run(self, user):
        balance = 0

        invoice_method = GetInvoices(paid=True)
        for invoice in await user.exec(invoice_method):
            if (invoice.payee == user.username):
                balance += invoice.amount
            if (invoice.payer == user.username):
                balance -= (invoice.amount + invoice.fee)

        if user.bitcoin_address:
            onchain_txfer_method = GetOnchainTxs(min_confirmations=3)
            for transaction in await user.exec(onchain_txfer_method):
                # Valid onchain btc transactions sent to this user's address
                # Debit user's account balance
                balance += transaction['amount']

        locked_payments_method = GetLockedPayments()
        for invoice in await user.exec(locked_payments_method):
            # for each locked payment (invoice that has been sent but not validated)
            # Credit user's account balance
            balance -= invoice['amount'] + \
                math.floor(invoice['amount'] * 0.01)  # fee limit

        return balance
