"""
File for resolving types that can branch from UserResponse
this includes: UserResponse (Union), User, and Error
""" 
from typing import Optional
from datetime import ( datetime, timedelta )
from ariadne import ObjectType, UnionType
from code.classes.user import User
from code.classes.error import Error

USER_RESPONSE = UnionType('UserResponse')

@USER_RESPONSE.type_resolver
def r_user_response(obj, *_):
    if isinstance(obj, Error):
        return 'Error'
    if isinstance(obj, User):
        return 'User'


USER = ObjectType('User')

@USER.field('username')
def r_username(obj: User, _) -> Optional[str]:
    return obj.username

@USER.field('password')
def r_password(obj: User, _) -> Optional[str]:
    return obj.password

@USER.field('accessToken')
async def r_access_token(obj: User, info) -> str:
    access_json = {
        'token': await obj.get_token(token_type='access'),
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + timedelta(minutes=15)
    }
    return info.context.jwt.encode(access_json, kind='access')

@USER.field('refreshToken')
async def r_refresh_token(obj: User, info) -> str:
    refresh_json = {
        'token': await obj.get_token(token_type='refresh'),
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + timedelta(days=7)
    }
    return info.context.jwt.encode(refresh_json, kind='refresh')

