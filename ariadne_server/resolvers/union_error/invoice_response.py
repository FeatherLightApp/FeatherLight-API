from ariadne import UnionType
from classes.error import Error

USER_INVOICE_RESPONSE = UnionType('UserInvoiceResponse')
PAY_INVOICE_RESPONSE = UnionType('PayInvoiceResponse')


@USER_INVOICE_RESPONSE.type_resolver
@PAY_INVOICE_RESPONSE.type_resolver
def r_add_invoice_response(obj, _, resolve_type):
    if isinstance(obj, Error):
        return 'Error'
    if getattr(obj, 'payment_hash', None) or obj.get('payment_hash'):
        if str(resolve_type) == 'PayInvoiceResponse':
            return 'PaidInvoice'
        if str(resolve_type) == 'UserInvoiceResponse':
            return 'UserInvoice'