from .abstract_user_method import AbstractMethod
from ...helpers.mixins import LoggerMixin
from ...helpers.async_future import make_async
from ...context import BITCOIND, LND
from ...models import User as DB_User
from ... import rpc_pb2 as ln

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
        user_obj = await DB_User.query.get(user.userid)
        assert user_obj
        # return address if it exists
        if (address := user_obj.bitcoin_address):
            return address

        #  create a new address
        request = ln.NewAddressRequest(type=0)
        response = await make_async(LND.stub.NewAddress.future(request, timeout=5000))
        address = response.address
        await user_obj.update(address=address).apply()
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