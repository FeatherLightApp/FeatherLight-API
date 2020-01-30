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
    """


def test_app():
    with TestClient(app) as client:
        user1 = make_user(client)
        user2 = make_user(client)
        assert user1[0] != user2[0] and user1[1] != user2[1]




test_app()
