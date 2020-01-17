"""import all types"""
from .query import query
from .mutation import mutation
from .tokenpayload import token_payload
# from .addinvoicepayload import add_invoice_payload
from .union import invoice
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
    token_payload,
    # add_invoice_payload,
    invoice,
    # local_invoice,
    # route_hint,
    # hop_hint,
    # features_entry,
    # feature
]
