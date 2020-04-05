from ariadne import UnionType
from classes.error import Error

LOGOUT_RESPONSE = UnionType('LogoutResponse')

@LOGOUT_RESPONSE.type_resolver
def r_logout_response(obj, *_):
    if isinstance(obj, Error):
        return 'Error'
    return 'Boolean'
