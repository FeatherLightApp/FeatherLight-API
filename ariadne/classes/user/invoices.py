import json
import rpc_pb2 as ln
from helpers.async_future import make_async
from.abstract_user_method import AbstractMethod
from context import LND
import models

class GetUserInvoices(AbstractMethod):
    """Method for retriving a user's invoices, either paid or unpaid"""

    def __init__(self, only_paid: bool = True, limit: int = 0):
        self.only_paid = only_paid
        self.limit = limit


    async def run(self, user):
        """
        retrives invoices (payment requests) for current user from redis and returns 
        them with payment state based on gRPC query.
        Side Effect: adds true lnd invoices as paid in redis
        Internal invoices are marked as paid on payment send
        """

        invoices = []
        # TODO test if this is possible else do for x in await 
        async for invoice in models.Invoice.objects.filter(payee=user.userid).limit(self.limit).all():

            req = ln.PayReqString(pay_req=invoice.payment_request)
            decoded = await make_async(
                    LND.stub.DecodePayReq.future(req, timeout=5000)
            )

            # Determine if invoice has been paid

            if not invoice.paid:
                # if not paid check lnd to see if its paid in lnd db
                # convert hex serialized payment hash to bytes
                

                req = ln.PaymentHash(r_hash=bytes.fromhex(invoice_json['r_hash']))
                lookup_info = await make_async(LND.stub.LookupInvoice.future(req, timeout=5000))

                if lookup_info.state == 1:
                    # invoice is paid update state in db
                    await invoice.update(paid=True)

                
            # invoice_json['amount'] = decoded.num_satoshis
            # invoice_json['expiry'] = decoded.expiry
            # invoice_json['timestamp'] = decoded.timestamp
            # invoice_json['kind'] = 'user_invoice'
            # invoice_json['memo'] = decoded.description
            # # TODO find fix for this
            # invoice_json['payment_hash'] = invoice_json['r_hash']
            
            invoices.append(invoice)
        # if only paid is false return all results else return only settled ammounts
        return [invoice for invoice in invoices if not self.only_paid or invoice.paid]