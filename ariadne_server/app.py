"""define app entry point"""
from starlette.applications import Starlette
from ariadne.asgi import GraphQL
from .context import LND, REDIS, GINO
from .resolvers.schema import SCHEMA


APP = Starlette(
    debug=True,
    on_startup=[LND.initialize, REDIS.initialize, GINO.initialize],
    on_shutdown=[REDIS.destroy, GINO.destroy]
)

APP.mount('/graphql', GraphQL(SCHEMA, debug=True))
