from ariadne import ObjectType

pay_invoice_payload = ObjectType('PayInvoicePayload')

@pay_invoice_payload.field('ok')
def r_ok(obj, info):
    if obj and not isinstance(obj, str):
        return True
    return False

@pay_invoice_payload.field('error')
def r_error(obj, info):
    if isinstance(obj, str):
        return obj
    return None


@pay_invoice_payload.field('')