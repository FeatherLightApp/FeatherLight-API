import pytest
from ariadne import graphql

@pytest.mark.asyncio()
@pytest.mark.parametrize('role', ['ADMIN', 'USER'])
async def test_create_user(role, schema, context):
    context['request'].headers['x-real-ip'] = 'otherip'
    response = await graphql(
        schema,
        {
            'query': open('queries/createUser.graphql').read(),
            'variables': {
                'role': role
            }
        },
        context_value=context,
        debug=True
    )
    r = response[1]['data']['createUser']
    assert r['username']
    assert r['password']
    assert r['role'] == role
    assert len(r['invoices']) == 0
    assert r['balance'] == 0
    assert r['btcAddress']
    assert r['created']
