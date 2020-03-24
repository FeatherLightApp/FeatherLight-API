from ariadne import UnionType
from ...classes.user import User
from ...classes.error import Error

_TOKEN_RESPONSE = UnionType('TokenResponse')

@_TOKEN_RESPONSE.type_resolver
def r_token_response(obj, *_) -> str:
    if isinstance(obj, Error):
        return 'Error'
    if isinstance(obj, str):
        return 'TokenPayload'


_USER_RESPONSE = UnionType('UserResponse')

@_USER_RESPONSE.type_resolver
def r_user_response(obj, *_):
    if isinstance(obj, Error):
        return 'Error'
    if isinstance(obj, User):
        return 'User'


_add_invoice_response = UnionType('AddInvoiceResponse')
_pay_invoice_response = UnionType('PayInvoiceResponse')


@_add_invoice_response.type_resolver
@_pay_invoice_response.type_resolver
def r_add_invoice_response(obj, _, resolve_type):
    if isinstance(obj, Error):
        return 'Error'
    if getattr(obj, 'payment_hash', None) or obj.get('payment_hash'):
        if str(resolve_type) == 'PayInvoiceResponse':
            return 'PaidInvoice'
        if str(resolve_type) == 'AddInvoiceResponse':
            return 'UserInvoice'


_wallet_response = UnionType('WalletResponse')

@_wallet_response.type_resolver
def r_wallet_response(obj, *_):
    if isinstance(obj, Error):
        return 'Error'
    return 'WalletBalance'


UNION = [
    _TOKEN_RESPONSE,
    _USER_RESPONSE,
    _add_invoice_response,
    _pay_invoice_response,
    _wallet_response
]
