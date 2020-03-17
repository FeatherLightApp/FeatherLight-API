from ariadne import UnionType
from code.classes.user import User
from code.classes.error import Error

_TOKEN_RESPONSE = UnionType('TokenResponse')

@_TOKEN_RESPONSE.type_resolver
def r_token_response(obj, *_) -> str:
    if isinstance(obj, Error):
        return 'Error'
    if isinstance(obj, str):
        return 'TokenPayload'


_USER_RESPONSE = UnionType('UserResponse')

@_USER_RESPONSE.type_resolver
def r_user_response(obj, info, resolve_type):
    if isinstance(obj, Error):
        return 'Error'
    if isinstance(obj, User):
        return 'User'
        

_ADD_INVOICE_RESPONSE = UnionType('AddInvoiceResponse')

@_ADD_INVOICE_RESPONSE.type_resolver
def r_add_invoice_response(obj, *_):
    if isinstance(obj, Error):
        return 'Error'
    if isinstance(obj, dict) and obj.get('r_hash'):
        return 'AddInvoicePayload'


_PAY_INVOICE_RESPONSE = UnionType('PayInvoiceResponse')

@_PAY_INVOICE_RESPONSE.type_resolver
def r_pay_invoice_response(obj, *_):
    if isinstance(obj, Error):
        return 'Error'
    return 'PayInvoicePayload'

UNION = [
    _TOKEN_RESPONSE,
    _USER_RESPONSE,
    _ADD_INVOICE_RESPONSE,
    _PAY_INVOICE_RESPONSE
]