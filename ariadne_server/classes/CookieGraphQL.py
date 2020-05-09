from ariadne.asgi import GraphQL
from starlette.responses import JSONResponse
from helpers.mixins import LoggerMixin

_logger = LoggerMixin()

class CookieGraphql(GraphQL):
    """ class to attach cookies to refresh requests"""
    async def graphql_http_server(self, request):
        res: JSONResponse = await GraphQL.graphql_http_server(self, request)
        if b'"__typename":"AuthPayload"' in res.body and b'"refresh":' in res.body:
            chop = res.body.split(b'"refresh":"')
            token = chop[1].split(b'"', maxsplit=1)[0]
            res.set_cookie(
                'refresh',
                token.decode('utf-8'),
                max_age=604800, #1 week
                secure=True,
                domain='dev.seanaye.ca',
                samesite='none',
                httponly=True
            )
        elif b'"logout":null' in res.body:
            res.set_cookie(
                'refresh',
                '',
                max_age=-1,
                secure=True,
                domain='dev.seanaye.ca',
                samesite='none',
                httponly=True
            )
        return res
