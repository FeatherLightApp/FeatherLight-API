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
        """get the calculated balance for the user"""
        calculated_balance = 0

        # get  offchain invoices added by the user
        for inv in await self.get_user_invoices(only_paid=True):
            calculated_balance += inv.amt

        for tx in await self.get_onchain_txs():
            # Valid onchain btc transactions sent to this user's address
            # Debit user's account balance
            calculated_balance += tx['amount'] * 100000000 # convert btc amount to sats
                
        for invoice in await self.get_offchain_txs():
            # for each dict in list of invoices paid by this user
            # Credit user's account balance
            calculated_balance -= invoice['value']

        for invoice in await self.get_locked_payments():
            # for each locked payment (invoice that has been sent but not validated)
            # Credit user's account balance
            calculated_balance -= invoice['amount'] + floor(invoice['amount'] * 0.01) #fee limit

        return calculated_balance


    async def add_invoice(self, memo, amt):
        """
        add invoice and associate user with hash in redis
        stores json representation of rpc protobuf in redis array
        """
        # TODO add suport for more custom invoices
        request = ln.Invoice(
            memo=memo,
            value=amt,
            expiry=3600*24
        )
        response = await make_async(self._lightning.AddInvoice.future(request, timeout=5000))
        output = protobuf_to_dict(response)
        output['r_hash'] = response.r_hash.hex()
        #change the bytes object to hex string for json serialization
        await self._redis.rpush(f"userinvoices_for_{self.userid}", json.dumps(output))
        # add hex encoded bytes hash to redis
        await self._redis.set(f"payment_hash_{output['r_hash']}", self.userid)
        return output


    async def get_user_invoices(self, only_paid=True):
        """
        retrives invoices (payment requests) for current user from redis and returns 
        them with payment state based on gRPC query.
        Side Effect: adds true lnd invoices as paid in redis

        Pseudo code

        Get payment hash associated with user
        for each hash lookup invoice
        determine if paid internally or externally via redis
        elif determine paid externally via lnd grpc
            if paid mark as paid in redis
        return invoices
        """

        invoices = []
        for payments_json_bytes in await self._redis.lrange(f"userinvoices_for_{self.userid}", 0, -1):
            #decode bytes string and parse into json of AddInvoice Response grpc
            invoice_json = json.loads(payments_json_bytes.decode('utf-8'))

            decoded = await make_async(
                self._lightning.decodePayReq.future(invoice_json.get('payment_request'), timeout=5000)
            )

            # Determine if invoice has been paid via redis using hex encoded string of payment hash
            invoice_json['ispaid'] = bool(await self._redis.get(f"is_paid_{invoice_json['r_hash']}"))

            if not invoice_json['ispaid']:
                # if not paid from redis check lnd to see if its paid in lnd db
                # convert hex serialized payment hash to bytes
                

                req = ln.PaymentHash(r_hash=bytes.fromhex(invoice_json['r_hash']))
                lookup_info = await make_async(self._lightning.lookupInvoice.future(req, timeout=5000))

                invoice_json['ispaid'] = lookup_info.state == 1
                if invoice_json['ispaid']:
                    #invoice has actually been paid, cache this in redis
                    await self._redis.set(f"is_paid_{invoice_json['r_hash']}")
                
            invoice_json['amt'] = decoded.num_satoshis
            invoice_json['expiry'] = decoded.expiry
            invoice_json['timestamp'] = decoded.timestamp
            invoice_json['kind'] = 'user_invoice'

            invoices.append(invoice_json)
        # if only paid is false return all results else return only settled ammounts
        return [invoice for invoice in invoices if not only_paid or invoice.get('ispaid')]

            
            


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
        """
        Return incoming onchain btc transactions
        retrives the valid transcations for a user based on bitcoind json response
        defaults to returning txs with >= 5 confirmations 
        """
        assert self.address
        txs = (await self._bitcoind.req('listtransactions', params={
            'label': self.userid,
            'count': 10000,
            'skip': 0,
            'include_watchonly': True
        })).get('result') or []

        def valid_tx(tx):
            confirmed = tx.get('confirmations') >= min_confirmations
            valid_address = tx.get('address') == self.address
            receive = tx.get('category') == 'receive'
            return confirmed and valid_address and receive

        return [tx for tx in txs if valid_tx(tx)]


    async def get_offchain_txs(self) -> list:
        """
        Return offchain outgoing payments sent by this user
        return offchain invoices that were paid by this user and stored in redis via save_paid_invoice
        """
        result = []
        ranges = await self._redis.lrange('paid_invoices_for_' + self.userid, 0, -1)
        """item is a byte encoded json representation of processSendPaymentResponse"""
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


    async def get_locked_payments(self):
        """
        retrives the locked payments for a user
        locked payments are outbound transactions that have not yet been accepted
        this is used to calculate a users balance correctly before tranctaions has been settled
        """
        payments = await self._redis.lrange('locked_payments_for_' + self.userid, 0, -1)
        result = []
        for paym in payments:
            try:
                data = json.loads(paym.decode('utf-8'))
                result.append(data)
            except json.decoder.JSONDecodeError as error:
                self.logger.critical(error)
        return result

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

        self.logger.critical(f"processed response: {payment}")

        return payment
