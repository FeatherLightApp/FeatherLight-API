from secrets import token_hex
import pytest
from ariadne import graphql


@pytest.mark.asyncio
@pytest.mark.dependency(depends=['test_create_user'])
async def test_login(schema, context):
    query = '''
        mutation login($username: String! password: String!) {
            login(username: $username password: $password) {
                __typename
                ... on User {
                    role
                    btcAddress
                    balance
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
        assert r['role'] == user['role']
        assert r['btcAddress'] == user['btcAddress']
        assert r['balance'] == 0

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
