from .abstract_user_method import AbstractMethod
from code.helpers.mixins import LoggerMixin
from code.helpers.async_future import make_async
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
        if not (address := await user.ctx.redis.get('bitcoin_address_for_' + user.userid)):
            request = ln.NewAddressRequest(type=0)
            response = await make_async(user.ctx.lnd.NewAddress.future(request, timeout=5000))
            address = response.address
            await user.ctx.redis.set('bitcoin_address_for_' + user.userid, address)
            self.logger.info(f"Created address: {address} for user: {user.userid}")
            import_response = await user.ctx.bitcoind.req(
                'importaddress',
                params={
                    'address': address, 
                    'label': user.userid,
                    'rescan': False
                }
            )
            return address
        return address.decode('utf-8')