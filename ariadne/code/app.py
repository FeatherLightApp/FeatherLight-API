"""define app entry point"""
import json
from code.resolvers.schema import SCHEMA
from code.classes.context import Context
from starlette.applications import Starlette
from ariadne.asgi import GraphQL


CTX = Context(json.loads(open('code/app_config.json').read()))

APP = Starlette(
    debug=True,
    on_startup=[CTX.async_init, CTX.smoke_tests],
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
