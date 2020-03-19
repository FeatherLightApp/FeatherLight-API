"""define app entry point"""
import json
from resolvers.schema import SCHEMA
import context
from starlette.applications import Starlette
from ariadne.asgi import GraphQL



APP = Starlette(
    debug=True,
    on_startup=[context.LND.initialize, context.REDIS.initialize],
    on_shutdown=[context.REDIS.destroy]
)

APP.mount(
    '/graphql',
    GraphQL(
        SCHEMA,
        debug=True
    )
)
