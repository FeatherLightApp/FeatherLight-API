"""import all types"""
from .query import QUERY
from .mutation import MUTATION
# from .addinvoicepayload import add_invoice_payload
from .union import invoice
from .subscription import subs
from .user_response import USER_RESPONSE, USER
from .enum import ERROR_TYPE
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
    ERROR_TYPE,
    # add_invoice_payload,
    invoice,
    subs,
    # local_invoice,
    # route_hint,
    # hop_hint,
    # features_entry,
    # feature
]
