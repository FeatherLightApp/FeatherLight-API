"""define app entry point"""
from starlette.applications import Starlette
from ariadne.asgi import GraphQL
from context import LND, REDIS, GINO, PUBSUB
from resolvers.schema import SCHEMA


APP = Starlette(
    debug=True,
    on_startup=[LND.initialize, REDIS.initialize, GINO.initialize, PUBSUB.initialize],
    on_shutdown=[LND.destroy, REDIS.destroy, GINO.destroy, PUBSUB.destroy]
)

APP.mount('/graphql', GraphQL(SCHEMA, debug=True))
