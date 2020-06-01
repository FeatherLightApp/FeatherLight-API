from typing import List
from ariadne import ObjectType
from helpers.crypto import attenuate


ATTENUATED_MACAROON = ObjectType("AttenuatedMacaroon")


@ATTENUATED_MACAROON.field("caveats")
def r_caveats(obj: List[str], *_) -> List[str]:
    return obj


@ATTENUATED_MACAROON.field("macaroon")
def r_macaroon(obj: List[str], info, *_) -> str:
    # TODO allow for multiple caveats
    macaroon = (
        info.context["request"].headers.get("Authorization").replace("Bearer ", "")
    )
    caveat = f"action = {obj[0]}"
    return attenuate(macaroon, [caveat])
