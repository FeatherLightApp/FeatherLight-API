from datetime import ( datetime, timedelta )
from ariadne import ObjectType
from code.classes.User import User

token_payload = ObjectType('TokenPayload')

@token_payload.field('ok')
def r_ok(obj, _):
    if isinstance(obj, User):
        return True
    return False

@token_payload.field('error')
def  r_error(obj, _):
    if isinstance(obj, str):
        return obj
    return None

@token_payload.field('access')
def r_access(obj, info):
    if isinstance(obj, User):
        access = {
            'token': obj.userid,
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(minutes=15)
        }
        return info.context.jwt.encode(access, kind='access')
    return None

@token_payload.field('refresh')
def r_refresh(obj, info):
    if isinstance(obj, User):
        refresh = {
            'token': obj.userid,
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(days=7)
        }
        return info.context.jwt.encode(refresh, kind='refresh')
    return None
