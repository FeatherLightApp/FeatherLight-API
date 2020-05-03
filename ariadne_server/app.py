"""define app entry point"""
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from classes.CookieGraphQL import CookieGraphql
from context import LND, REDIS, GINO
from resolvers.schema import SCHEMA
from helpers.mixins import LoggerMixin

_logger = LoggerMixin()


middleware = [
    Middleware(
        CORSMiddleware,
        allow_origins=['http://127.0.0.1:3000', 'http://localhost:3000', 'https://inspiring-lichterman-9da30e.netlify.app'],
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
        GINO.initialize,
        _logger.logger.info('app init')
    ],
    on_shutdown=[LND.destroy, REDIS.destroy, GINO.destroy],
    middleware=middleware
)

APP.mount('/graphql', CookieGraphql(SCHEMA, debug=True))
