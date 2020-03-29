from secrets import token_hex
import pytest
from classes.error import Error
from resolvers.types.mutation import (
    r_create_user,
    r_auth,
    r_get_token
)
from resolvers.types.token_payload import (
    r_access_token,
    r_refresh_token
)
from helpers.crypto import decode as decode_jwt

@pytest.mark.asyncio
@pytest.mark.parametrize('role', ['ADMIN', 'USER'])
async def test_create_user(role):
    user_obj = await r_create_user(role=role)
    assert user_obj.id
    assert user_obj.username
    assert user_obj.password
    assert user_obj.role == role
    pytest.users.append({
        'obj': user_obj
    })




@pytest.mark.asyncio
async def test_login():
    for user in pytest.users:
        u = user.get('obj')
        login = r_auth(username=u.username, password=u.password)
        assert login.role == u.role
        #test login failure
        login2 = r_auth(username=u.username, password=token_hex(10))
        assert isinstance(login2, Error)


def test_get_tokens():
    for user in pytest.users:
        u = user.get('obj')
        access_token = r_access_token(u)
        assert access_token
        assert decode_jwt(access_token, kind='access')
        refresh_token = r_refresh_token(u)
        assert refresh_token
        assert decode_jwt(refresh_token, kind='refresh')
        user['access'] = access_token
        user['refresh'] = refresh_token


@pytest.mark.asyncio
@pytest.mark.usefixtures('info')
def test_refresh_access_token(info):
    for user in pytest.users:
        #set refresh token on fake info obj
        info.context['request'].cookies['refresh'] = user.get('refresh')
        user_obj = r_get_token(None, info)
        assert user['obj'] == user_obj

        #test invalid token, set the refresh token as access token
        info.context['request'].cookies['refresh'] = user.get('access')
        user_obj = r_get_token(None, info)
        assert isinstance(user_obj, Error)
