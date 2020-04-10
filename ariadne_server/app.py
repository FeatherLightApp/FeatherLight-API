"""define app entry point"""
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from ariadne.asgi import GraphQL
from context import LND, REDIS, GINO
from resolvers.schema import SCHEMA

middleware = [
    Middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_methods=['*'],
        allow_headers=['*'],
        allow_credentials=True
    )
]

APP = Starlette(
    debug=True,
    on_startup=[LND.initialize, REDIS.initialize, GINO.initialize],
    on_shutdown=[LND.destroy, REDIS.destroy, GINO.destroy],
    middleware=middleware
)

APP.mount('/graphql', GraphQL(SCHEMA, debug=True))
