from time import time
from ariadne import ObjectType
from classes.user import User
from helpers.crypto import bake

TOKEN_PAYLOAD = ObjectType('TokenPayload')


@TOKEN_PAYLOAD.field('access')
def r_access_token(user: User, *_) -> str:
    # 900 seconds is 15 minutes
    caveats = [
        # f'expiry = {int(time()) + 900}',
        f'user = {user.username}',
        f'role = {user.role}',
    ]
    return bake(user=user, caveats=caveats).serialize()


@TOKEN_PAYLOAD.field('refresh')
def r_refresh_token(user: User, *_) -> str:
    caveats = [
        f'expiry = {int(time()) + 604800}',
        f'user = {user.username}',
        'action = REFRESH'
    ]
    return bake(user=user, caveats=caveats).serialize()