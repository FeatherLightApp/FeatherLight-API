from time import time
from typing import Tuple, List
from ariadne import ObjectType
from classes.user import User
from helpers.crypto import bake, attenuate

AUTH_PAYLOAD = ObjectType('AuthPayload')

@AUTH_PAYLOAD.field('access')
def r_access_token(user: User, info) -> str:
    # 900 seconds is 15 minutes
    caveats = [
        # f'expiry = {int(time()) + 900}',
        f'user = {user.username}',
        f'role = {user.role}',
        f"origin = {info.context['request'].headers['origin']}"
    ]
    return bake(user=user, caveats=caveats)

@AUTH_PAYLOAD.field('refresh')
def r_refresh_token(user: User, info) -> str:
    caveats = [
        f'expiry = {int(time()) + 604800}',
        f'user = {user.username}',
        'action = REFRESH',
        f"origin = {info.context['request'].headers['origin']}"
    ]
    return bake(user=user, caveats=caveats)


ATTENUATED_MACAROON = ObjectType('AttenuatedMacaroon')

@ATTENUATED_MACAROON.field('caveats')
def r_caveats(obj: List[str], *_) -> List[str]:
    return obj


@ATTENUATED_MACAROON.field('macaroon')
def r_macaroon(obj: List[str], info, *_) -> str:
    # TODO allow for multiple caveats
    macaroon = info.context['request'].headers.get('Authorization').replace('Bearer ', '')
    caveat = f'action = {obj[0]}'
    return attenuate(macaroon, [caveat])
