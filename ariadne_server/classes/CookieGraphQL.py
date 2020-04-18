from ariadne.asgi import GraphQL
from starlette.responses import JSONResponse
from helpers.mixins import LoggerMixin

_logger = LoggerMixin()

class CookieGraphql(GraphQL):
    """ class to attach cookies to refresh requests"""
    async def graphql_http_server(self, request):
        res: JSONResponse = await GraphQL.graphql_http_server(self, request)
        if b'"__typename":"TokenPayload"' in res.body and b'"refresh":' in res.body:
            chop = res.body.split(b'"refresh":"')
            token = chop[1].split(b'"', maxsplit= 1)[0]
            _logger.logger.critical('applying cookie')
            _logger.logger.critical(token)
            res.set_cookie(
                'refresh',
                token.decode('utf-8'),
                expires=604800, #1 week
                secure=True,
                domain='dev.seanaye.ca',
                samesite='none',
                httponly=True
            ) 
        return res
