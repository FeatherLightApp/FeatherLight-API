"""import all types"""
from .query import QUERY
from .mutation import MUTATION
# from .addinvoicepayload import add_invoice_payload
from .union import UNION
from .subscription import subs
from .token_payload import TOKEN_PAYLOAD
from .user import USER 
from .scalar import SCALAR
from .interface import INTERFACE

TYPES = [
    *UNION,
    *SCALAR,
    *INTERFACE,
    QUERY,
    MUTATION,
    TOKEN_PAYLOAD,
    USER,
    # add_invoice_payload,
    subs,
    # local_invoice,
    # route_hint,
    # hop_hint,
    # features_entry,
    # feature
]
