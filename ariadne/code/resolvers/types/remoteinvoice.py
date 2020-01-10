from ariadne import ObjectType

remote_invoice = ObjectType('RemoteInvoice')
# TODO add route type from send payment GRPC response

@remote_invoice.field('error')
def r_error(obj, info):
    return obj.payment_error

@remote_invoice.field('preimage')
def r_preimage(obj, info):
    return obj.payment_preimage

@remote_invoice.field('route')
def r_route(obj, info):
    return obj.route

@remote_invoice.field('hash')
def r_hash(obj, info):
    return obj.hash

@remote_invoice.field('decoded')
def r_decoded(obj, info):
    return obj.decoded

@remote_invoice.field('payReq')
def r_pay_req(obj, info):
    return obj.pay_req
