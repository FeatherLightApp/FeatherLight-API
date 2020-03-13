"""file for resolving fields of UserResponse that are not handeld by default resolver"""
from ariadne import ObjectType
from code.classes.user import User

USER = ObjectType('User')

@USER.field('tokens')
def r_tokens(user: User, _):
    # return userid as string to tokenpayload resolver
    return user.userid
