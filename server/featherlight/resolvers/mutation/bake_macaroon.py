from typing import List
from ariadne import MutationType
from classes import User

MUTATION = MutationType()


@MUTATION.field("bakeMacaroon")
def r_bake_macaroon(user: User, *_, caveats: List[str]):
    return caveats
