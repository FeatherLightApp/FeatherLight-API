"""import all types"""
from .query import query
from .mutation import mutation
from .tokenpayload import token_payload
from .addinvoicepayload import add_invoice_payload

types = [
    query,
    mutation,
    token_payload,
    add_invoice_payload
]
