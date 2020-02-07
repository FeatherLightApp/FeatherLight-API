"""import all types"""
from .query import query
from .mutation import mutation
# from .addinvoicepayload import add_invoice_payload
from .union import invoice
from .tokenpayload import token_payload
from .subscription import subs
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

types = [
    query,
    mutation,
    # add_invoice_payload,
    invoice,
    token_payload,
    subs
    # local_invoice,
    # route_hint,
    # hop_hint,
    # features_entry,
    # feature
]
