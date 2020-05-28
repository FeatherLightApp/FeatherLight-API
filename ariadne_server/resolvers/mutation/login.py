from typing import Union

from ariadne import MutationType
from argon2.exceptions import VerificationError

from classes.user import User
from classes.error import Error
from context import ARGON

MUTATION = MutationType()

@MUTATION.field('login')
async def r_login(*_, username: str, password: str) -> Union[User, Error]:
    if not (user_obj := await User.get(username)):
        return Error('AuthenticationError', 'User not found')
    # verify pw hash
    try:
        ARGON.verify(user_obj.password_hash, password)
    except VerificationError:
        return Error('AuthenticationError', 'Incorrect password')

    if ARGON.check_needs_rehash(user_obj.password_hash):
        await user_obj.update(password_hash=ARGON.hash(password)).apply()

    return user_obj
