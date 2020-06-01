import pytest
from ariadne import graphql

pytestmark = pytest.mark.asyncio

async def test_meta_query(schema):
    res = await graphql(
        schema,
        {
            'query': open('queries/meta_info.graphql').read()
        }
    )
    r = res[1]['data']
    assert r['API'] == 'FeatherLight'
    assert r['version'] == '1.0'
    assert r['network'] == 'TESTNET'
