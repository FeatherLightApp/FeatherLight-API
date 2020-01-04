import aioredis
from ariadne import MutationType
from code.classes.User import User

mutation = MutationType()
# TODO add JWT support and expire tokens in redis

@mutation.field('create')
# TODO add post limiter?
async def r_create(obj, info):
    u = User(info.context.redis, info.context.bitcoind, info.context.lightning)
    await u.create()
    return {
        'login': u.get_login(),
        'password': u.get_pw()
    }
