import pytest
from ariadne import graphql
from .context import FakeContext

@pytest.fixture(scope='session')
async def dummy_user(schema):
    response = await graphql(
        schema,
        {
            'query': open('queries/createUser.graphql'),
            'variables': {
                'role': 'USER'
            }
        },
        context_value=FakeContext()
    )
    return response[1]['data']['createUser']


@pytest.fixture(scope='session')
async def dummy_admin(schema):
    response = await graphql(
        schema,
        {
            'query': open('queries/createUser.graphql'),
            'variables': {
                'role': 'ADMIN'
            }
        },
        context_value=FakeContext()
    )
    return response[1]['data']['createUser']

