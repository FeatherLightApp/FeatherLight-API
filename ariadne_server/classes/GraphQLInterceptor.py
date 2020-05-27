from ariadne.asgi import GraphQL
from starlette.responses import JSONResponse
from helpers.mixins import LoggerMixin

_logger = LoggerMixin()

def extract_value(key, data):
    split_at = f'"{key}":"'.encode('utf-8')
    chop = data.split(split_at)
    return chop[1].split(b'"', maxsplit=1)[0]

class GraphqlInterceptor(GraphQL):
    """ class to attach cookies to refresh requests"""
    async def graphql_http_server(self, request):
        res: JSONResponse = await GraphQL.graphql_http_server(self, request)
        # set cookies on login
        if b'"__typename":"AuthPayload"' in res.body and b'"refresh":' in res.body:
            token = extract_value('refresh', res.body)
            res.set_cookie(
                'refresh',
                token.decode('utf-8'),
                max_age=604800, #1 week
                secure=True,
                # TODO extract only domain name from os.environ.get('ENDPOINT')
                domain='featherlight.app',
                samesite='none',
                httponly=True
            )
        # set cookies on logout
        elif b'"logout":null' in res.body:
            res.set_cookie(
                'refresh',
                '',
                max_age=-1,
                secure=True,
                domain='featherlight.app',
                samesite='none',
                httponly=True
            )
        # set status code and headers on lsat
        elif b'"__typename":"LSATPayload"' in res.body:
            res.status_code = 402
            macaroon = extract_value('macaroon', res.body)
            pay_req = extract_value('paymentRequest', res.body)
            res.headers['WWW-Authenticate'] = f'LSAT macaroon="{macaroon.decode("utf-8")}", invoice="{pay_req.decode("utf-8")}"'
        return res
