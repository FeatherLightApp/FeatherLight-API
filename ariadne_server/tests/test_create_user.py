from secrets import token_hex
import pytest
from ariadne import graphql
from classes.error import Error
from helpers.crypto import decode as decode_jwt

@pytest.mark.asyncio()
@pytest.mark.dependency()
@pytest.mark.parametrize('role', [('ADMIN'), ('USER')])
@pytest.mark.usefixtures('schema')
async def test_create_user(role, schema):
    query = '''
        mutation createUser($role: String){
            createUser(role: $role) {
                __typename
                ... on User {
                    username
                    password
                    role
                    btcAddress
                    tokens {
                        access
                        refresh
                    }
                    balance
                    invoices {
                        paymentHash
                    }
                }
            }
        }
    '''
    response = (await graphql(
        schema,
        {
            'query': query,
            'variables': {
                'role': role
            }
        }
    ))['data']['createUser']
    assert response['username']
    assert response['password']
    assert response['role'] == role
    assert len(response['invoices']) == 0
    assert response['balance'] == 0
    assert response['btcAddress']
    pytest.users.append(response)
