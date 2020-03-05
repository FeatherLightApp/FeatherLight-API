import functools
from typing import Callable, Optional, Any
from inspect import iscoroutinefunction
from code.classes.user import User
from code.classes.error import Error
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError

def authenticate(func: Callable) -> Callable:
    @functools.wraps(func)
    async def authwrapper(obj: Optional[Any], info, **kwargs: Any) -> dict:
        if not (header := info.context.req.headers.get('Authorization')):
            return Error('AuthenticationError', 'No access token sent. You are not logged in')
        try:
            if not (u := await User.from_jwt(ctx=info.context, token=header.replace('Bearer ', ''), kind='access')):
                return Error('AuthenticationError', 'Could not perform user lookup')
            elif iscoroutinefunction(func):
                # Pass the user into an asynchronous resolver and await
                return await func(obj, info, **kwargs, user=u)
            else:
                # Pass the user into a synchronous resolver
                return func(obj, info, **kwargs, user=u)
        except ExpiredSignatureError:
            return Error('AuthenticationError', 'Access token has expired')
        except InvalidTokenError:
            return Error('AuthenticationError', 'Invalid access token')
    return authwrapper
