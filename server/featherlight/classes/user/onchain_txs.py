from .abstract_user_method import AbstractMethod
from .btc_address import GetBTCAddress
from context import BITCOIND


class GetOnchainTxs(AbstractMethod):
    def __init__(self, min_confirmations=5, limit: int = 1000, offset: int = 0):
        self._min_confirmations = min_confirmations
        self._limit = limit
        self._offset = offset

    # fct to convert btc amt to sats
    @staticmethod
    def _format(tx):
        tx["amount"] = int(tx["amount"] * 100000000)
        return tx

    async def run(self, user):
        """
        Return incoming onchain btc transactions
        retrives the valid transcations for a user based on bitcoind json response
        """
        # if the user doesn't have a bitcoin address generated, return
        if not user.bitcoin_address:
            return []

        get_address_method = GetBTCAddress()
        address = await user.exec(get_address_method)
        assert address, f"Cannot get btc address for {user.username}"
        txs = (
            await BITCOIND.req(
                "listtransactions",
                params={
                    "label": user.username,
                    "count": self._limit,
                    "skip": self._offset,
                    "include_watchonly": True,
                },
            )
        ).get("result") or []

        def valid_tx(tx):
            # determine if the btc transaction is valid for this user
            confirmed = tx.get("confirmations") >= self._min_confirmations
            valid_address = tx.get("address") == address
            receive = tx.get("category") == "receive"
            return confirmed and valid_address and receive

        return [self._format(tx) for tx in txs if valid_tx(tx)]
