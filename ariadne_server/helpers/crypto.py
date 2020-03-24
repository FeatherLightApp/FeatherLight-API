from hashlib import sha256
import json
from typing import Union
from jwt import encode as encode_jwt
from jwt import decode as decode_jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from ..classes.error import Error

KEYS = json.loads(open('keys.json').read())

def encode(jsn: dict, kind: str) -> str:
    """encodes valid json as a jwt"""
    return encode_jwt(
        jsn,
        KEYS.get(f"{kind}_secret"),
        algorithm='HS256'
    ).decode('utf-8')


def decode(token: str, kind: str) -> Union[dict, Error]:
    """decodes jwt into json(python dict)"""
    try:
        return decode_jwt(
            token,
            KEYS.get(f"{kind}_secret"),
            algorithms='HS256'
        )
    except ExpiredSignatureError:
        return Error('AuthenticationError', 'Token has expired')
    except InvalidTokenError:
        return Error('AuthenticationError', 'Invalid token')

def hash_string(string):
    """returns hex digest of string"""
    hasher = sha256()
    hasher.update(string.encode('utf-8'))
    return hasher.digest().hex()
