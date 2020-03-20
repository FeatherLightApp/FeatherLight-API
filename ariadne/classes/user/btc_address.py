from .abstract_user_method import AbstractMethod
from helpers.mixins import LoggerMixin
from helpers.async_future import make_async
from context import BITCOIND, REDIS, LND
import rpc_pb2 as ln

class GetBTCAddress(AbstractMethod, LoggerMixin):

    def __init__(self):
        LoggerMixin().__init__()

    async def run(self, user):
        """
        return bitcoin address of user. If the address does not exist
        asynchronously generate a new lightning address
        gRPC Response: NewAddressResponse
        see https://api.lightning.community/#newaddress
        for more info

        """
        assert user.userid
        if not (address := await REDIS.conn.get('bitcoin_address_for_' + user.userid)):
            request = ln.NewAddressRequest(type=0)
            response = await make_async(LND.NewAddress.future(request, timeout=5000))
            address = response.address
            await REDIS.conn.set('bitcoin_address_for_' + user.userid, address)
            self.logger.info(f"Created address: {address} for user: {user.userid}")
            import_response = await BITCOIND.req(
                'importaddress',
                params={
                    'address': address, 
                    'label': user.userid,
                    'rescan': False
                }
            )
            return address
        return address.decode('utf-8')