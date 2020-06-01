from ariadne import MutationType
from classes.user import User

MUTATION = MutationType()


@MUTATION.field("refreshMacaroons")
def r_refresh_macaroons(user: User, *_) -> User:
    # pass user into token payload resolver
    return user
