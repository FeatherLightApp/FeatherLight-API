import os
from time import time
from typing import List
from starlette.requests import Request
from pymacaroons import Macaroon, Verifier
from classes.user import User
from helpers.mixins import LoggerMixin

_logger = LoggerMixin()

def bake(user: User, caveats: List[str]) -> str:
    m_obj = Macaroon(
        location=os.environ.get('ENDPOINT'),
        identifier=user.username,
        key=user.key
    )

    for caveat in caveats:
        m_obj.add_first_party_caveat(caveat)

    return m_obj.serialize()

def verify(
        macaroon: Macaroon,
        key: bytes,
        roles: List[str],
        caveats: List[str],
        used: int,
        req: Request
) -> bool:
    assert macaroon
    v_obj = Verifier()

    v_obj.satisfy_exact(f'user = {macaroon.identifier}')
    for role in roles:
        v_obj.satisfy_exact(f'role = {role}')

    # satisfy specific actions in the API
    for caveat in caveats:
        v_obj.satisfy_exact(f'action = {caveat}')

    # satify same origin restrictions
    v_obj.satisfy_exact(f"origin = {req.headers['origin']}")

    # satisfy macaroon with time expiry
    v_obj.satisfy_general(
        lambda x: x.split(' = ')[0] == 'expiry' and  \
            int(x.split(' = ')[1]) > time()
    )

    # satisfy macaroon with limited uses
    v_obj.satisfy_general(
        lambda x: x.split(' = ')[0] == 'uses' and \
            int(x.split(' = ')[1]) > used
    )

    return bool(v_obj.verify(macaroon, key))


def attenuate(
    macaroon: str,
    caveats: List[str]
) -> str:
    m_obj = Macaroon.deserialize(macaroon)

    for caveat in caveats:
        m_obj.add_first_party_caveat(caveat)
    
    return str(m_obj.serialize())
