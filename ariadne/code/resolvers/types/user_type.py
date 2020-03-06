"""
File for resolving types that can branch from UserResponse
this includes: UserResponse (Union), User, and Error
""" 
from typing import Optional
from ariadne import ObjectType
from code.classes.user import User
from code.classes.error import Error


USER = ObjectType('User')

@USER.field('username')
def r_username(obj: User, _) -> Optional[str]:
    return obj.username

@USER.field('password')
def r_password(obj: User, _) -> Optional[str]:
    return obj.password


@USER.field('btcAddress')
async def r_btc_address(obj: User, _) -> str:
    return await obj.get_address()


@USER.field('tokens')
def r_tokens(obj: User, _) -> str:
    # pass user to token payload resolver
    return obj