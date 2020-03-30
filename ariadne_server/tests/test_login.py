from secrets import token_hex
import pytest
from ariadne import graphql
from helpers.crypto import decode as decode_jwt


@pytest.mark.asyncio
@pytest.mark.last
async def test_login(schema, context):
    query = '''
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
    for user in pytest.users:
        response = await graphql(
            schema,
            {
                'query': query,
                'variables': {
                    'username': user['username'],
                    'password': user['password']
                }
            },
            context_value=context.rand_client(),
            debug=True
        )
        r = response[1]['data']['login']
        assert decode_jwt(r['access'], kind='access')['role'] == user['role']
        assert decode_jwt(r['refresh'], kind='refresh')

    response = await graphql(
        schema,
        {
            'query': query,
            'variables': {
                'username': pytest.users[0]['username'],
                'password': token_hex(10)
            }
        },
        context_value=context.rand_client(),
        debug=True
    )
    r = response[1]['data']['login']

    assert r['errorType'] == 'AuthenticationError'
    assert r['message'] == 'Incorrect password'

    response = await graphql(
        schema,
        {
            'query': query,
            'variables': {
                'username': token_hex(10),
                'password': pytest.users[0]['password']
            }
        },
        context_value=context.rand_client(),
        debug=True
    )
    r = response[1]['data']['login']
    assert r['errorType'] == 'AuthenticationError'
    assert r['message'] == 'User not found'
