from typing import Optional
from ariadne import ObjectType
from context import LND
import rpc_pb2 as ln

CHANNEL_PAYLOAD = ObjectType('ChannelPayload')

@CHANNEL_PAYLOAD.field('openChannels')
async def open_channels(
    self,
    *_,
    active: bool = False,
    inactive: bool = False,
    public: bool = False,
    private: bool = False,
    peer: Optional[bytes] = None
):
    req = ln.ListChannelsRequest(
        active_only=active,
        inactive_only=inactive,
        public_only=public,
        private_only=private
    )
    r = await LND.stub.ListChannels(req)
    return r.channels


@CHANNEL_PAYLOAD.field('pendingChannels')
async def pending_channels(self, *_):
    req = ln.PendingChannelsRequest()
    return await LND.stub.PendingChannels(req)
