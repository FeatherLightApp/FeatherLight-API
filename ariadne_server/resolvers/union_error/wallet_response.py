from ariadne import UnionType
from classes.error import Error

WALLET_RESPONSE = UnionType('BalanceResponse')


@WALLET_RESPONSE.type_resolver
def r_wallet_response(obj, *_):
    if isinstance(obj, Error):
        return 'Error'
    return 'NodeBalance'
