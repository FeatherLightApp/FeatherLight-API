from datetime import (datetime, timedelta)
from ariadne import ObjectType
from classes.user import User
from helpers.crypto import encode

TOKEN_PAYLOAD = ObjectType('TokenPayload')


@TOKEN_PAYLOAD.field('accessToken')
def r_access_token(user: User, _) -> str:
    access_json = {
        'id': user.id,
        'role': user.role,
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + timedelta(minutes=15)
    }
    return encode(access_json, kind='access')


@TOKEN_PAYLOAD.field('refreshToken')
def r_refresh_token(user: User, _) -> str:
    refresh_json = {
        'id': user.id,
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + timedelta(days=7)
    }
    return encode(refresh_json, kind='refresh')
