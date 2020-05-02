from .token_response import TOKEN_RESPONSE as _TOKEN_RESPONSE
from .invoice_response import USER_INVOICE_RESPONSE as _USER_INVOICE_RESPONSE
from .invoice_response import PAY_INVOICE_RESPONSE as _PAY_INVOICE_RESPONSE
from .wallet_response import WALLET_RESPONSE as _WALLET_RESPONSE
from .user_response import USER_RESPONSE as _USER_RESPONSE
from .user_response import NEW_USER_RESPONSE as _NEW_USER_RESPONSE
from .channel_response import CHANNEL_RESPONSE as _CHANNEL_RESPONSE

UNION_ERROR = [
    _TOKEN_RESPONSE,
    _USER_INVOICE_RESPONSE,
    _PAY_INVOICE_RESPONSE,
    _WALLET_RESPONSE,
    _USER_RESPONSE,
    _NEW_USER_RESPONSE,
    _CHANNEL_RESPONSE
]