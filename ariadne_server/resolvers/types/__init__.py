"""import all types"""
from .query import QUERY
from .mutation import MUTATION
# from .addinvoicepayload import add_invoice_payload
from .union import UNION
from .subscription import subs
from .token_payload import TOKEN_PAYLOAD
from .scalar import SCALAR
from .interface import INTERFACE
from .balance_payload import _balance_payload, _channel_balance

TYPES = [
    *UNION,
    *SCALAR,
    *INTERFACE,
    QUERY,
    MUTATION,
    TOKEN_PAYLOAD,
    _balance_payload,
    _channel_balance,
    # add_invoice_payload,
    subs,
    # local_invoice,
    # route_hint,
    # hop_hint,
    # features_entry,
    # feature
]
