"""define app entry point"""
from json import loads
from starlette.applications import Starlette
from ariadne.asgi import GraphQL
from code.resolvers.schema import schema
from code.classes import Context

conf = loads(open('code/app_config.json').read())
keys = loads(open('code/keys.json').read())

conf.update(keys)

ctx = Context(conf)

app = Starlette(
    debug=True,
    on_startup=[ctx.init_redis, ctx.smoke_tests],
    on_shutdown=[ctx.destroy]
)
app.mount(
    '/graphql',
    GraphQL(
        schema,
        debug=True,
        context_value=ctx
    )
)
