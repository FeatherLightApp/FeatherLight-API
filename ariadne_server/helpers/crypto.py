from time import time
from typing import List
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
        use: str
) -> bool:
    assert macaroon
    v_obj = Verifier()

    v_obj.satisfy_exact(f'user = {macaroon.identifier}')
    v_obj.satisfy_general(
        lambda x: x.split(' = ')[0] == 'expiry' and  \
            int(x.split(' = ')[1]) > time()
    )
    for role in roles:
        print(f'adding validation for caveat role = {role}')
        v_obj.satisfy_exact(f'role = {role}')

    for action in actions:
        print(f'adding validation for caveat action = {action}')
        v_obj.satisfy_exact(f'action = {action}')

    v_obj.satisfy_exact(f'use = {use}')
    
    return v_obj.verify(macaroon, key)
