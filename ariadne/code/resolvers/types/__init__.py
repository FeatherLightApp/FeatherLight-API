"""import all types"""
from .query import QUERY
from .mutation import MUTATION
# from .addinvoicepayload import add_invoice_payload
from .union import USER_RESPONSE, TOKEN_RESPONSE, ADD_INVOICE_RESPONSE
from .subscription import subs
from .token_payload import TOKEN_PAYLOAD
from .user import USER 
# from .localinvoice import (
#     local_invoice,
#     route_hint,
#     hop_hint,
#     features_entry,
#     feature
# )
# from .remoteinvoice import (
#     remote_invoice
#     # TODO Route type
# )

TYPES = [
    QUERY,
    MUTATION,
    USER_RESPONSE,
    TOKEN_RESPONSE,
    TOKEN_PAYLOAD,
    ADD_INVOICE_RESPONSE,
    USER,
    # add_invoice_payload,
    subs,
    # local_invoice,
    # route_hint,
    # hop_hint,
    # features_entry,
    # feature
]
