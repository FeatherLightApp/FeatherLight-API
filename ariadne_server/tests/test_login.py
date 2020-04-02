from secrets import token_hex
import pytest
from ariadne import graphql
from helpers.crypto import decode as decode_jwt

pytestmark = pytest.mark.asyncio

login_query = open('queries/login.graphql').read()

async def user_login(schema, context, user):
    response = await graphql(
        schema,
        {
            'query': login_query,
            'variables': {
                'username': user['username'],
                'password': user['password']
            }
        },
        context_value=context,
        debug=True
    )
    r = response[1]['data']['login']
    assert decode_jwt(r['access'], kind='access')['role'] == user['role']
    assert decode_jwt(r['refresh'], kind='refresh')
    return True


@pytest.mark.usefixtures('dummy_user')
async def test_user_login(schema, context, dummy_user):
    assert await user_login(schema, context, dummy_user)


@pytest.mark.usefixtures('dummy_admin')
async def test_admin_login(schema, context, dummy_admin):
    assert await user_login(schema, context, dummy_admin)



@pytest.mark.usefixtures('dummy_user')
async def test_invalid_password(schema, context, dummy_user):
    response = await graphql(
        schema,
        {
            'query': login_query,
            'variables': {
                'username': dummy_user['username'],
                'password': token_hex(10)
            }
        },
        context_value=context,
        debug=True
    )
    r = response[1]['data']['login']

    assert r['errorType'] == 'AuthenticationError'
    assert r['message'] == 'Incorrect password'


@pytest.mark.usefixtures('dummy_user')
async def test_invalid_username(schema, context, dummy_user):
    response = await graphql(
        schema,
        {
            'query': login_query,
            'variables': {
                'username': token_hex(10),
                'password': dummy_user['password']
            }
        },
        context_value=context,
        debug=True
    )
    r = response[1]['data']['login']
    assert r['errorType'] == 'AuthenticationError'
    assert r['message'] == 'User not found'
