import json
import rpc_pb2 as ln
from code.helpers.async_future import make_async
from.abstract_user_method import AbstractMethod

class GetUserInvoices(AbstractMethod):
    """Method for retriving a user's invoices, either paid or unpaid"""

    def __init__(self, only_paid: bool = True, start: int = 0, end: int = -1):
        self.only_paid = only_paid
        self.start = start
        self.end = end


    async def run(self, user):
        """
        retrives invoices (payment requests) for current user from redis and returns 
        them with payment state based on gRPC query.
        Side Effect: adds true lnd invoices as paid in redis
        Internal invoices are marked as paid on payment send
        """

        invoices = []
        for payments_json_bytes in await user.ctx.redis.lrange(
            f"userinvoices_for_{user.userid}", self.start, self.end
        ):
            #decode bytes string and parse into json of AddInvoice Response grpc
            invoice_json = json.loads(payments_json_bytes.decode('utf-8'))

            req = ln.PayReqString(pay_req=invoice_json.get('payment_request'))
            decoded = await make_async(
                    user.ctx.lnd.DecodePayReq.future(req, timeout=5000)
            )

            # Determine if invoice has been paid via redis using hex encoded string of payment hash
            invoice_json['ispaid'] = bool(await user.ctx.redis.get(f"is_paid_{invoice_json['r_hash']}"))

            if not invoice_json['ispaid']:
                # if not paid from redis check lnd to see if its paid in lnd db
                # convert hex serialized payment hash to bytes
                

                req = ln.PaymentHash(r_hash=bytes.fromhex(invoice_json['r_hash']))
                lookup_info = await make_async(user.ctx.lnd.LookupInvoice.future(req, timeout=5000))

                invoice_json['ispaid'] = lookup_info.state == 1
                if invoice_json['ispaid']:
                    #invoice has actually been paid, cache this in redis
                    await user.ctx.redis.set(f"is_paid_{invoice_json['r_hash']}", 1)
                
            invoice_json['amt'] = decoded.num_satoshis
            invoice_json['expiry'] = decoded.expiry
            invoice_json['timestamp'] = decoded.timestamp
            invoice_json['kind'] = 'user_invoice'

            invoices.append(invoice_json)
        # if only paid is false return all results else return only settled ammounts
        return [invoice for invoice in invoices if not self.only_paid or invoice.get('ispaid')]