from ariadne import UnionType
from classes.error import Error
from classes.user import User

USER_RESPONSE = UnionType('UserResponse')


@USER_RESPONSE.type_resolver
def r_user_response(obj, *_):
    if isinstance(obj, Error):
        return 'Error'
    if isinstance(obj, User):
        return 'User'


NEW_USER_RESPONSE = UnionType('NewUserResponse')
@NEW_USER_RESPONSE.type_resolver
def r_new_user_response(obj, *_):
    if isinstance(obj, Error):
        return 'Error'
    if isinstance(obj, User):
        return 'NewUser'
