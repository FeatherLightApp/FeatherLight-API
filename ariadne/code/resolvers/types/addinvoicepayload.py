# from ariadne import ObjectType

# add_invoice_payload = ObjectType('AddInvoicePayload')

# @add_invoice_payload.field('ok')
# def r_ok(obj, info):
#     if obj and obj.payment_request:
#         return True
#     return False

# @add_invoice_payload.field('error')
# def r_erro(obj, info):
#     if obj and obj.payment_request:
#         info.context.logger.critical(
#             'could not add invoice. Got {} with request: {}'
#                 .format(obj, info.context.req)
#         )
#         return 'An error has occured while adding invoice'
#     return None

# @add_invoice_payload.field('hash')
# def r_hash(obj, info):
#     if obj and obj.r_hash:
#         return obj.r_hash.hex()
#     return None


# @add_invoice_payload.field('paymentReq')
# def r_paymentreq(obj, info):
#     if obj and obj.payment_request:
#         return obj.payment_request
#     return None


# @add_invoice_payload.field('addIndex')
# def r_add_index(obj, info):
#     if obj and obj.add_index:
#         return int(obj.add_index)
#     return None