"""import all types"""
from .query import QUERY
from .mutation import MUTATION
# from .addinvoicepayload import add_invoice_payload
from .union import invoice, USER_RESPONSE, TOKEN_RESPONSE
from .subscription import subs
from .user_type import USER
from .token_payload import TOKEN_PAYLOAD
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
    USER,
    TOKEN_RESPONSE,
    TOKEN_PAYLOAD,
    # add_invoice_payload,
    invoice,
    subs,
    # local_invoice,
    # route_hint,
    # hop_hint,
    # features_entry,
    # feature
]
