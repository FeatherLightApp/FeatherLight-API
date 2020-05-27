"""define app entry point"""
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from classes import GraphqlInterceptor
from context import LND, REDIS, GINO
from resolvers.schema import SCHEMA
from helpers.mixins import LoggerMixin

_logger = LoggerMixin()


middleware = [
    Middleware(
        CORSMiddleware,
        allow_origins=[
            'http://127.0.0.1:3000',
            'http://localhost:3000',
            'https://featherlight.app', 
            'chrome-extension://iolgemahcebdonemnjepfomopcgikklg'
        ],
        allow_methods=['*'],
        allow_headers=['*'],
        allow_credentials=True
    )
]

APP = Starlette(
    debug=True,
    on_startup=[
        LND.initialize,
        REDIS.initialize,
        GINO.initialize
    ],
    on_shutdown=[LND.destroy, REDIS.destroy, GINO.destroy],
    middleware=middleware
)

APP.mount('/graphql', GraphqlInterceptor(SCHEMA, debug=True))
