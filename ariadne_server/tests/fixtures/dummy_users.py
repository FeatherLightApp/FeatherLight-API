from time import time
import pytest
from ariadne import graphql

@pytest.fixture(scope='session')
async def dummy_user(schema, context):
    response = await graphql(
        schema,
        {
            'query': open('queries/createUser.graphql'),
            'variables' {
                'role': 'USER'
            }
        }
    )
    return response[1]['data']['createUser']


@pytest.fixture(scope='session')
async def dummy_user(schema, context):
    response = await graphql(
        schema,
        {
            'query': open('queries/createUser.graphql'),
            'variables' {
                'role': 'ADMIN'
            }
        }
    )
    return response[1]['data']['createUser']

