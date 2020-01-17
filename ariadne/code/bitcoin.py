"""Class for running bitcoin rpc requests"""
from httpx import AsyncClient

class Bitcoin(AsyncClient):
    """Subclass for making btcd rpc requests"""
    def __init__(self, config):
        super().__init__()
        self._host = config['host']
        self._port = config['port']
        self._certpath = config['certpath']
        self._user = config['user']
        self._pass = config['pass']

    async def req(self, method, params=None, reqiq=None):
        """make a request to bitcoin rpc and return response json async"""
        return await self.post(
            f'https://{self._host}:{self._port}',
            json={'method': method, 'params': params, 'id': reqiq},
            verify=self._certpath,
            auth=(self._user, self._pass),
            headers={'Content-Type': 'application/json'}
        ).json()
