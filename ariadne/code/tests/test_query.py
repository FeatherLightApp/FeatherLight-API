from starlette.testclient import TestClient
from app import app

def make_user(client):
    create_user_query = """
    mutation {
        create {
            ok
            error
            login
            password
        }
    }
    """
    res = client.post('/graphql/', json={'query': create_user_query})
    assert res.status_code == 200
    js = res.json()
    assert js['data']['create']['ok']
    return js['data']['create']['login'], js['data']['create']['password']

def login(client, user):
    login_query = """
    query {
        login(user: "%s" password: "%s"}) {
            ok
            error
            access
            refresh
        }
    }
    """ % (user[0], user[1])
    res = client.post('/graphql/', json={'query': login_query})
    assert res.status_code == 200
    js res.json()
    assert (access := js['data']['login']['access'])
    assert (refress := js['data']['login']['refresh'])
    return access, refresh


def test_app():
    with TestClient(app) as client:
        user1 = make_user(client)
        user2 = make_user(client)
        assert user1[0] != user2[0] and user1[1] != user2[1]
        token1 = login(client, user1)
        token2 = login(client, user2)






test_app()
