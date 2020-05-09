from ariadne import QueryType
from context import LND
from grpclib.exceptions import GRPCError
import rpc_pb2 as ln


QUERY = QueryType()

@QUERY.field('decodeInvoice')
async def r_decode_invoice(*_, invoice: str):
    request = ln.PayReqString(pay_req=invoice.replace('lightning:', ''))
    try:
        return await LND.stub.DecodePayReq(request)
    except GRPCError:
        return None
