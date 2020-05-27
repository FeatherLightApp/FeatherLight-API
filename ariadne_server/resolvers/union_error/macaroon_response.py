from ariadne import UnionType
from pymacaroons import Macaroon
from classes.user import User
from classes.error import Error

_MACAROON_RESPONSE = UnionType('MacaroonResponse')


@_MACAROON_RESPONSE.type_resolver
def r_token_response(obj, *_) -> str:
    if isinstance(obj, Error):
        return 'Error'
    elif isinstance(obj, User):
        return 'AuthPayload'
    return ''

_ATTENUATED_MACAROON_RESPONSE = UnionType('AttenuatedMacaroonResponse')

@_ATTENUATED_MACAROON_RESPONSE.type_resolver
def r_attenuated_response(obj, *_) -> str:
    if isinstance(obj, Error):
        return 'Error'
    return 'AttenuatedMacaroon'


MACAROON_RESPONSES = [
    _MACAROON_RESPONSE,
    _ATTENUATED_MACAROON_RESPONSE
]