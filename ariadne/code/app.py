"""define app entry point"""
import json
from code.resolvers.schema import SCHEMA
from code.classes.context import Context, LND, REDIS
from starlette.applications import Starlette
from ariadne.asgi import GraphQL

config = json.loads(open('code/app_config.json').read())

CTX = Context(config)

APP = Starlette(
    debug=True,
    on_startup=[CTX.async_init, CTX.smoke_tests, LND.initialize, REDIS.initialize],
    on_shutdown=[CTX.destroy]
)
APP.mount(
    '/graphql',
    GraphQL(
        SCHEMA,
        debug=True,
        context_value=CTX
    )
)
