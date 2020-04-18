from time import time
from typing import List
from starlette.requests import Request
from pymacaroons import Macaroon, Verifier
from classes.user import User

def bake(user: User, caveats: List[str]) -> str:
    m_obj = Macaroon(
        location='lumenwallet.io',
        identifier=user.username,
        key=user.key
    )

    for caveat in caveats:
        m_obj.add_first_party_caveat(caveat)

    return m_obj

def verify(
        macaroon: Macaroon,
        key: bytes,
        roles: List[str],
        actions: List[str],
        req: Request
) -> bool:
    assert macaroon
    v_obj = Verifier()

    v_obj.satisfy_exact(f'user = {macaroon.identifier}')
    for role in roles:
        v_obj.satisfy_exact(f'role = {role}')

    for action in actions:
        v_obj.satisfy_exact(f'action = {action}')

    v_obj.satisfy_general(
        lambda x: x.split(' = ')[0] == 'expiry' and  \
            int(x.split(' = ')[1]) > time()
    )

    v_obj.satisfy_exact(f"origin = {req.headers['origin']}")

    return v_obj.verify(macaroon, key)
