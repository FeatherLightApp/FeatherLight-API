"""import all types"""
from .query import QUERY
from .mutation import MUTATION
# from .addinvoicepayload import add_invoice_payload
from .union import UNION
from .token_payload import TOKEN_PAYLOAD
from .scalar import SCALAR
from .interface import INTERFACE
from .balance_payload import BALANCE_PAYLOAD
from .subscription.root import EXPORT as sub_export

TYPES = [
    *UNION,
    *SCALAR,
    *INTERFACE,
    QUERY,
    MUTATION,
    TOKEN_PAYLOAD,
    BALANCE_PAYLOAD,
    # add_invoice_payload,
    *sub_export
    # local_invoice,
    # route_hint,
    # hop_hint,
    # features_entry,
    # feature
]
