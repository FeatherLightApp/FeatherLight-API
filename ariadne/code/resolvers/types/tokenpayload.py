from datetime import (
    datetime,
    timedelta
)
from ariadne import ObjectType

token_payload = ObjectType('TokenPayload')

@token_payload.field('ok')
def r_ok(obj, info):
    if obj:
        return True
    return False


@token_payload.field('access')
def r_access_token(obj, info):
    if obj:
        access_json = {
            'token': u.access_token,
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(minutes=15)
        }
        return context.jwt.encode(access_json, kind='access')
    return None


@token_payload.field('refresh')
def r_refresh_token(obj, info):
    if obj:
        refresh_json = {
            'token': u.refresh_token,
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(days=7)
        }
        return context.jwt.encode(refresh_json, kind='refresh')
    return None


@token_payload.field('error')
def r_error(obj, info):
    if not obj:
        return 'Bad credentials'
    return None

