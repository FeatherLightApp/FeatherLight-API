from ariadne import UnionType
from classes.user import User
from classes.error import Error

TOKEN_RESPONSE = UnionType('TokenResponse')


@TOKEN_RESPONSE.type_resolver
def r_token_response(obj, *_) -> str:
    if isinstance(obj, Error):
        return 'Error'
    if isinstance(obj, User):
        return 'TokenPayload'
