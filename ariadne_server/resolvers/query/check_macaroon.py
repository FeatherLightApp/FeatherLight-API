from typing import List
from ariadne import QueryType
from resolvers.directives import AuthDirective
from classes import Error

QUERY = QueryType()

@QUERY.field('checkMacaroon')
async def r_macaroon_check(_, info, caveats: List[str]):
    def extract_macaroon(info):
        auth = info.context['request'].headers['Authorization']
        if not auth:
            return None
        return auth.replace('Bearer ', '')
    directive = AuthDirective('authchecker', {'caveats': caveats}, None, None, None)
    directive.get_macaroon = extract_macaroon
    res = directive.check_auth(info)
    if isinstance(res, Error):
        return res
    return None


