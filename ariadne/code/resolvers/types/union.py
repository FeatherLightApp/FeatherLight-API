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

@TOKEN_RESPONSE.type_resolver
def r_token_response(obj, *_) -> str:
    if isinstance(obj, Error):
        return 'Error'
    if isinstance(obj, str):
        return 'TokenPayload'


USER_RESPONSE = UnionType('UserResponse')

@USER_RESPONSE.type_resolver
def r_user_response(obj, info, resolve_type):
    if isinstance(obj, Error):
        return 'Error'
    if isinstance(obj, User):
        return 'User'
        

ADD_INVOICE_RESPONSE = UnionType('AddInvoiceResponse')

@ADD_INVOICE_RESPONSE.type_resolver
def r_add_invoice_response(obj, *_):
    if isinstance(obj, Error):
        return 'Error'
    if isinstance(obj, dict) and obj.get('r_hash'):
        return 'AddInvoicePayload'
