from datetime import ( datetime, timedelta )
from ariadne import ObjectType
from code.classes.user import User
from code.helpers.crypto import encode

TOKEN_PAYLOAD = ObjectType('TokenPayload')

@TOKEN_PAYLOAD.field('accessToken')
def r_access_token(userid: str, _) -> str:
    access_json = {
        'id': userid,
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + timedelta(minutes=15)
    }
    return encode(access_json, kind='access')

@TOKEN_PAYLOAD.field('refreshToken')
def r_refresh_token(userid: str, _) -> str:
    refresh_json = {
        'id': userid,
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + timedelta(days=7)
    }
    return encode(refresh_json, kind='refresh')
