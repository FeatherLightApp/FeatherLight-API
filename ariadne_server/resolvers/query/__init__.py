from .info import QUERY as info
from .bypass import QUERY as bypass
from .decode_invoice import QUERY as decode_invoice
from .check_macaroon import QUERY as check_macaroon
from .version import QUERY as version
from .api import QUERY as api

QUERY = [
    info,
    bypass,
    decode_invoice,
    check_macaroon,
    version,
    api
]
