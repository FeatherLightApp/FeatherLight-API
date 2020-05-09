from secrets import token_bytes
from ariadne import MutationType
from classes.user import User

MUTATION = MutationType()

@MUTATION.field('logout')
async def r_logout (user: User, *_) -> None:
    await user.update(key=token_bytes(32)).apply()
    return None
