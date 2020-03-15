"""File to define method for retriving offchain txs"""
import json
from .abstract_user_method import AbstractMethod

class GetOffchainTxs(AbstractMethod):
    """Method for retrieving offchain txs of a user"""

    def __init__(self, start: int = 0, end: int = -1):
        # requesting end of 0 returns last tx
        self.start = start
        self.end = end


    async def run(self, user):
        """
        Return offchain invoices that were paid by this user and stored in redis via save_paid_invoice
        """
        result = []
        ranges = await user.ctx.redis.lrange('paid_invoices_for_' + user.userid, self.start, self.end)
        #item is a byte encoded json representation of processSendPaymentResponse
        for item in ranges:
            invoice = json.loads(item.decode('utf-8'))

            if invoice.get('payment_route'):
                invoice['fee'] = int(invoice['payment_route']['total_fees'])
                invoice['value'] = int(invoice['payment_route']['total_fees']) \
                    + invoice['payment_route']['total_amt']
                # check if invoice had mSats
                if (invoice['payment_route'].get('total_amt_msat') and \
                    invoice['payment_route']['total_amt_msat'] / 1000 != int(invoice['payment_route']['total_amt'])
                ):
                    # account for mSats
                    # value is fees plus max of either value plus one to account for extra sat
                    invoice['value'] = invoice['payment_route']['total_fees'] \
                        + max(int(invoice['payment_route']['total_amt_msat'] / 1000), int(invoice['payment_route']['total_amt'])) + 1
            else:
                invoice['fee'] = 0

            if invoice.get('decoded'):
                invoice['timestamp'] = invoice['decoded']['timestamp']
                invoice['memo'] = invoice['decoded']['description']

            # TODO ensure invoice is processed in processSendPaymentReponse and payment_preimage is encoded to hex when saved
            # if invoice['payment_preimage']:
            #     invoice['payment_preimage'] = ast.literal_eval(invoice['payment_preimage']).

            del invoice['payment_error']
            del invoice['payment_route']
            del invoice['pay_req']
            del invoice['decoded']
            self.logger.warning(f"Appending paid invoice {invoice}")
            result.append(invoice)

        return result