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
        

_INVOICE_RESPONSE = UnionType('AddInvoiceResponse')

@_INVOICE_RESPONSE.type_resolver
def r_add_invoice_response(obj, *_):
    if isinstance(obj, Error):
        return 'Error'
    if getattr(obj, 'r_hash', None):
        return 'AddInvoicePayload'

UNION = [
    _TOKEN_RESPONSE,
    _USER_RESPONSE,
    _INVOICE_RESPONSE
]