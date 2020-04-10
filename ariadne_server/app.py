"""define app entry point"""
from starlette.applications import Starlette
from starlette.responses import PlainTextResponse
from starlette.routing import Route
from starlette.endpoints import HTTPEndpoint
from ariadne.asgi import GraphQL
from context import LND, REDIS, GINO, PUBSUB
from resolvers.schema import SCHEMA

class CorsEndpoint(HTTPEndpoint):
    async def _template(self, request):
        return PlainTextResponse('Hello World')

    get = _template
    post = _template

routes = [
    Route('/cors', CorsEndpoint)
]

APP = Starlette(
    debug=True,
    on_startup=[LND.initialize, REDIS.initialize, GINO.initialize],
    on_shutdown=[LND.destroy, REDIS.destroy, GINO.destroy],
    routes=routes
)

APP.mount('/graphql', GraphQL(SCHEMA, debug=True))
