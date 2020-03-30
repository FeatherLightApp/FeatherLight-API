from secrets import token_hex
import pytest
from ariadne import graphql
from helpers.crypto import decode as decode_jwt

pytestmark = pytest.mark.asyncio

login_query = '''
    mutation login($username: String! $password: String!) {
        login(username: $username password: $password) {
            __typename
            ... on TokenPayload {
                access
                refresh
            }
            ... on Error {
                errorType
                message
            }
        }
    }
'''

async user_login(schema, context, user):
    response = await graphql(
        schema,
        {
            'query': login_query,
            'variables': {
                'username': dummy_user.username,
                'password': dummy_user.password
            }
        },
        context_value=context.rand_client(),
        debug=True
    )
    r = response[1]['data']['login']
    assert decode_jwt(r['access'], kind='access')['role'] == user['role']
    assert decode_jwt(r['refresh'], kind='refresh')
    return True


@pytest.mark.usefixtures('dummy_user')
async def test_user_login(schema, context, dummy_user):
    assert user_login(schema, context, dummy_user)


async def test_admin_login(schema, context, admin_user):
    assert user_login(schema, context, admin_user)



@pytest.mark.usefixtures('dummy_user')
async def test_invalid_password(schema, context, dummy_user)
    response = await graphql(
        schema,
        {
            'query': login_query,
            'variables': {
                'username': dummy_user.username,
                'password': token_hex(10)
            }
        },
        context_value=context.rand_client(),
        debug=True
    )
    r = response[1]['data']['login']

    assert r['errorType'] == 'AuthenticationError'
    assert r['message'] == 'Incorrect password'


@pytest.mark.usefixtures('dummy_user')
async def test_invalid_username(schema, context, dummy_user)
    response = await graphql(
        schema,
        {
            'query': login_query,
            'variables': {
                'username': token_hex(10),
                'password': dummy_user.password
            }
        },
        context_value=context.rand_client(),
        debug=True
    )
    r = response[1]['data']['login']
    assert r['errorType'] == 'AuthenticationError'
    assert r['message'] == 'User not found'
