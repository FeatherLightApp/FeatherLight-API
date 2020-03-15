import json
from protobuf_to_dict import protobuf_to_dict
from code.helpers.async_future import make_async
from code.helpers.mixins import LoggerMixin
import rpc_pb2 as ln

class InvoiceManager(LoggerMixin):
    def __init__(self, *, redis, lightning, bitcoind, userid):
        assert userid
        super().__init__()
        self._redis = redis
        self._lightning = lightning
        self._bitcoind = bitcoind
        self.userid = userid
        self.address = None # this is set by calling get_address() on parent user class

    async def get_balance(self):






    async def get_user_invoices(self, only_paid=True):


            
            


        # ranges = await self._redis.lrange('payment_hash_for_' + self.userid, 0, -1)
        # result = []
        # for invoice in ranges:
        #     invoice_dict = json.loads(invoice)
        #     req = ln.PayReqString(pay_req=invoice_dict['payment_request'])
        #     decoded = await make_async(self._lightning.DecodePayReq.future(req, timeout=5000))
        #     invoice_ispaid = False
        #     if self.cache and decoded.paymenthash in self.cache['invoice_ispaid']:
        #         invoice_ispaid = True
        #     else:
        #         invoice_ispaid = bool(await self.get_payment_hash_paid(decoded.payment_hash))
        #     if not invoice_ispaid:
        #         utc_seconds = (datetime.utcnow() - datetime.datetime(1970, 1, 1)).total_seconds()
        #         if decoded and decoded.timestamp > (utc_seconds - 3600 * 24 * 5):
        #             # if invoice is not too old we query lnd to find out if its paid
        #             lookup_info = await self.lookup_invoice(decoded.paymenthash)
        #             if lookup_info.settled:
        #                 # invoice is actually already paid
        #                 await self.set_payment_hash_paid(decoded.paymenthash)
        #                 await self.clear_balance_cache()
            

        #     invoice_dict['amount'] = decoded.amount
        #     invoice_dict['expires'] = decoded.expires
        #     # TODO ^^ make sure this is correct
        #     invoice_dict['timestamp'] = decoded.timestamp
        #     invoice_dict['type'] = 'user_invoice'
        #     result.append(invoice_dict)

        # return result

    async def save_outoing_payment(self, invoice):
        """
        Mark a payment as paid outgoing in a user's account
        Save a paid lnd invoice. This could either be a true lnd invoice or a fake internal one
        """
        

    async def get_onchain_txs(self, min_confirmations: int=5) -> list:



    async def get_offchain_txs(self) -> list:
        


    async def get_locked_payments(self):


    def process_true_sent_payment(self, payment):
        """process a true lnd sent payment response from lnrpc.sendPayment"""
        if payment and payment.payment_route and payment.payment_route.total_amt_msat:
            # paid just now
            self._ispaid = True
            payment.payment_route.total_fees = payment.payment_route.total_fees \
                + floor(payment.payment_route.total_amt * Paym.fee())
            if self._bolt11:
                payment.pay_req = self._bolt11
            if self._decoded:
                payment.decoded = self._decoded

        if payment.payment_error and 'already paid' in payment.payment_error:
            # already paid
            self._ispaid = True
            if self._decoded:
                payment.decoded = self._decoded
                if self._bolt11:
                    payment.pay_req = self._bolt11
                # trying to guess the fee
                payment.payment_route = payment.payment_route if payment.payment_route else DotDict()
                payment.payment_route.total_fees = floor(self._decoded.num_satoshis * 0.01)
                payment.payment_route.total_amt = self._decoded.num_satoshis

        if payment.payment_error and 'unable to' in payment.payment_error:
            # failed to pay
            self._ispaid = False

        if payment.payment_error and 'FinalExpiryTooSoon' in payment.payment_error:
            self._ispaid = False

        if payment.payment_error and 'UnknownPaymentHash' in payment.payment_error:
            self._ispaid = False

        if payment.payment_error and 'payment is in transition' in payment.payment_error:
            self._ispaid = None # None is default but lets set it anyway

        self.logger.info(f"processed response: {payment}")

        return payment
