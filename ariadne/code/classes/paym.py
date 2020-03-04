# TODO Re-write or remove this file, few of its functions are used
"""define class for tracking payments"""
from datetime import datetime
from math import floor
from base64 import b64encode
from code.helpers.async_future import make_async
# from code.helpers.bolt11.address import Address
from code.helpers.mixins import DotDict
import rpc_pb2 as ln



class Paym:
    """Class for defining and making payments"""
    def __init__(self, redis, bitcoindrpc, lightning):
        self._redis = redis
        self._lightning = lightning
        self._bitcoindrpc = bitcoindrpc
        self._decoded = None
        self._bolt11 = False
        self._ispaid = None
        self._decoded_locally = None

    @staticmethod
    def fee():
        """returns fee"""
        return 0.003

    def set_invoice(self, bolt11):
        """sets the bolt11 invoice for the class"""
        self._bolt11 = bolt11

    async def decode_payreq_rpc(self, invoice):
        """Asynchronously tries to decode invoice string via rpc
        returns a gRPC Response: PayReq
        """
        request = ln.PayReqString(pay_req=invoice)
        response = await make_async(self._lightning.DecodePayReq.future(request, timeout=5000))
        self._decoded = response
        return response

    async def query_routes(self):
        """queries the routes"""
        if not self._bolt11:
            raise RuntimeError('bolt11 is not provided')
        if not self._decoded:
            await self.decode_payreq_rpc(self._bolt11)

        fee_limit = ln.FeeLimit(
            fixed=floor(self._decoded.num_satoshis * 0.01) + 1
        )
        request = ln.QueryRoutesRequest(
            pub_key=self._decoded.destination,
            amt=self._decoded.num_satoshis,
            final_cltv_delta=144,
            fee_limit=fee_limit,
        )
        return await make_async(self._lightning.QueryRoutes.future(request, timeout=5000))

    async def send_to_route_sync(self, routes):
        """attempt to send route"""
        if not self._bolt11:
            raise RuntimeError('bolt11 is not provided')
        if not self._decoded:
            await self.decode_payreq_rpc(self._bolt11)
        hash_bytes = b64encode(bytes.fromhex(self._decoded.payment_hash))
        request = ln.SendToRouteRequest(
            payment_hash=hash_bytes,
            routes=routes
        )

        return await make_async(self._lightning.SendToRouteSync.future(request, timeout=5000))

    def process_send_payment_response(self, payment):
        """process the sent payment"""
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

        return payment

    def get_is_paid(self):
        """getter method for the payment status"""
        return self._ispaid

    async def attempt_to_pay_route(self):
        """attempt to pay the route"""
        routes = await self.query_routes()
        return await self.send_to_route_sync(routes.routes)

    async def list_payments(self):
        """list the payments on the channel"""
        request = ln.ListPaymentsRequest()
        return await make_async(self._lightning.ListPayments.future(request, timeout=5000))

    async def is_expired(self):
        """determine if the invoice is expired"""
        if not self._bolt11:
            raise RuntimeError('bolt11 is not provided')
        decoded = await self.decode_payreq_rpc(self._bolt11)
        utc_seconds = (datetime.utcnow() - datetime.datetime(1970, 1, 1)).total_seconds()
        return decoded.timestamp + decoded.expiry < utc_seconds

    # def decode_payreq_local(self, payreq):
    #     """locally decode pay req"""
        # TODO make sure Address class align with attribute names of ln.DecodePayReq
        # self._decoded_locally = Address.from_string(payreq)

    async def get_payment_hash(self):
        """return the payment hash for the payment"""
        if not self._bolt11:
            raise RuntimeError('bolt11 is not provided')
        if not self._decoded:
            await self.decode_payreq_rpc(self._bolt11)

        return self._decoded.payment_hash
