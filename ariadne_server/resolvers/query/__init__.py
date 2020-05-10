from .info import QUERY as info
from .bypass import QUERY as bypass
from .decode_invoice import QUERY as decode_invoice
from .macaroon_check import QUERY as macaroon_check

QUERY = [
    info,
    bypass,
    decode_invoice,
    macaroon_check
]