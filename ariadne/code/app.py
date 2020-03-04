"""define app entry point"""
from json import loads
from code.resolvers.schema import SCHEMA
from code.classes.context import Context
from starlette.applications import Starlette
from ariadne.asgi import GraphQL

CONF = loads(open('code/app_config.json').read())
KEYS = loads(open('code/keys.json').read())

CONF.update(KEYS)

CTX = Context(CONF)

APP = Starlette(
    debug=True,
    on_startup=[CTX.init_redis, CTX.smoke_tests],
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
