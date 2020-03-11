from ariadne import UnionType
from code.classes.user import User
from code.classes.error import Error

invoice = UnionType('Invoice')


@invoice.type_resolver
def r_invoice_type(obj, _):
    if obj.hash:
        return 'RemoteInvoice'
    return 'LocalInvoice'

TOKEN_RESPONSE = UnionType('TokenResponse')
USER_RESPONSE = UnionType('UserResponse')

@TOKEN_RESPONSE.type_resolver
@USER_RESPONSE.type_resolver
def r_user_response(obj, info, resolve_type):
    info.context.logger.critical(resolve_type)
    if isinstance(obj, Error):
        return 'Error'
    if isinstance(obj, User):
        if str(resolve_type) == 'TokenResponse':
            return 'TokenPayload'
        if str(resolve_type) == 'UserResponse':
            return 'User'
        

ADD_INVOICE_RESPONSE = UnionType('AddInvoiceResponse')

@ADD_INVOICE_RESPONSE.type_resolver
def r_add_invoice_response(obj, _):
    if isinstance(obj, Error):
        return 'Error'
    if isinstance(obj, dict) and obj.get('paymentRequest'):
        return 'AddInvoicePayload'
