from datetime import ( datetime, timedelta )
from ariadne import ObjectType
from code.classes.user import User

TOKEN_PAYLOAD = ObjectType('TokenPayload')

@TOKEN_PAYLOAD.field('accessToken')
async def r_access_token(obj: User, info) -> str:
    access_json = {
        'id': obj.userid,
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + timedelta(minutes=15)
    }
    return info.context.jwt.encode(access_json, kind='access')

@TOKEN_PAYLOAD.field('refreshToken')
async def r_refresh_token(obj: User, info) -> str:
    refresh_json = {
        'id': obj.userid,
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + timedelta(days=7)
    }
    return info.context.jwt.encode(refresh_json, kind='refresh')