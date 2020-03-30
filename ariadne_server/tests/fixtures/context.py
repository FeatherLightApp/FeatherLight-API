from secrets import token_hex
import pytest


class Object:
    pass


class FakeContext(dict):
    
    def __init__(self):
        req_obj = Object()
        req_obj.cookies = {}
        req_obj.client = Object()
        req_obj.client.host = 'some_ip_address'
        req_obj.headers = {}

        self['request'] = req_obj

    def rand_client(self):
        self['request'].client.host = token_hex(5)
        return self


@pytest.fixture(autouse=True)
def context():
    return FakeContext()