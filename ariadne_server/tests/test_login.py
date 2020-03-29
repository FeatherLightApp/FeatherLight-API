import pytest
from ariadne import graphql


@pytest.mark.asyncio
@pytest.mark.dependency(depends=['test_create_user'])
async def test_login(schema):
    query='''
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
        response = (await graphql(
            schema,
            {
                'query': query,
                'variables': {
                    'username' user['username'],
                    'password': user['password']
                }
            }
        ))['data']['login']
        assert response['role'] == user['role']
        assert btcAddress == user['btcAddress']
        assert balance == 0

    response = (await graphql(
        schema,
        {
            'query': query,
            'variables': {
                'username': pytest.users[0]['username'],
                'password': token_hex(10)
            }
        }
    ))['data']['login']

    assert response['errorType'] == 'AuthenticationError'
    assert response['message'] == 'Incorrect password'

    response = (await graphql(
        schema,
        {
            'query': query,
            'variables': {
                'username': token_hex(10),
                'password': pytest.users[0]['password']
            }
        }
    ))['data']['login']
    assert response['errorType'] == 'AuthenticationError'
    assert response['message'] == 'User not found'
