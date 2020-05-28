from typing import Union
from ariadne import UnionType
from classes import Error
from models import LSAT

LSAT_REPONSE = UnionType('LSATResponse')

@LSAT_REPONSE.type_resolver
def r_lsat_response(obj: Union[LSAT, Error], *_) -> str:
    if isinstance(obj, Error):
        return 'Error'
    return 'LSATPayload'
