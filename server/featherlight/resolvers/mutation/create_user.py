from secrets import token_bytes, token_hex
from time import time
from ariadne import MutationType
from context import ARGON
from classes.user import User

MUTATION = MutationType()


@MUTATION.field("createUser")
async def r_create_user(*_, role: str = "USER") -> User:
    """create a new user and save to db"""
    # create api object
    password = token_hex(10)
    # save to db
    user = await User.create(
        key=token_bytes(32),
        username=token_hex(10),
        password_hash=ARGON.hash(password),
        role=role,
        created=time(),
    )
    # set password field on user to pass them their password 1 time
    user.password = password
    # return api object to resolver
    return user
