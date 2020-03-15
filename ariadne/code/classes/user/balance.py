import math
from .abstract_user_method import AbstractMethod
from .invoices import GetUserInvoices
from .onchain_txs import GetOnchainTxs
from .offchain_txs import GetOffchainTxs
from .locked_payments import GetLockedPayments

class GetBalance(AbstractMethod):
    """method to get the calculated balance for the user"""

    async def run(self, user):
        balance = 0
        
        #asking for 0 invoices returns all invoices
        invoice_method = GetUserInvoices(only_paid=True)
        for paid_invoice in await user.execute(invoice_method):
            balance += paid_invoice['amount']

        onchain_txfer_method = GetOnchainTxs(min_confirmations=3)
        for tx in await user.execute(onchain_txfer_method):
            # Valid onchain btc transactions sent to this user's address
            # Debit user's account balance
            balance += tx['amount']
                
        offchain_txfer_method = GetOffchainTxs()
        for invoice in await user.execute(offchain_txfer_method):
            # for each dict in list of invoices paid by this user
            # Credit user's account balance
            balance -= invoice['value']

        locked_payments_method = GetLockedPayments()
        for invoice in await user.execute(locked_payments_method):
            # for each locked payment (invoice that has been sent but not validated)
            # Credit user's account balance
            balance -= invoice['amount'] + math.floor(invoice['amount'] * 0.01) #fee limit

        return balance
