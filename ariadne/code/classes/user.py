"""module for defining the user class"""
import json
from typing import Union
from math import floor, ceil
from secrets import token_hex
from hashlib import sha256
from datetime import datetime
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from code.helpers.async_future import make_async
from code.helpers.mixins import LoggerMixin
from code.classes.lock import Lock
from code.classes.error import Error
from code.classes.invoice import InvoiceManager
import rpc_pb2 as ln


class User(LoggerMixin):
    """defines an instance of a user cache variable is only necessary in
    queries or mutations that call functions requiring the global cache values"""
    def __init__(self, ctx):
        super().__init__()
        self._redis = ctx.redis
        self._bitcoind = ctx.btcd
        self._lightning = ctx.lnd
        self.userid = None
        self.username = None
        self.password = None #only on newly created users. generated pw must be returned to user
        self.cache = ctx.cache
        self.invoice_manager = None


    @classmethod
    async def from_jwt(cls, ctx, token: str, kind: str) -> Union[Error, 'User']:
        """Factory method for creating instance from hex token"""
        try:
            jsn = ctx.jwt.decode(token, kind)
            this = cls(ctx)
            this.userid = jsn['id']
            this.invoice_manager = InvoiceManager(
                redis=this._redis,
                lightning=this._lightning,
                bitcoind=this.bitcoind,
                userid=this.userid
            )
            this.logger.info(f"initalized user: {this.userid}")
            return this
        except ExpiredSignatureError:
            return Error(error_type='AuthenticationError', message='Token has expired')
        except InvalidTokenError:
            return Error(error_type='AuthenticationError', message='Invalid JSON Web Token')


    @classmethod
    async def from_credentials(cls, ctx, username: str, password: str) -> Union[Error, 'User']:
        """factory method for instantiating from credentials"""
        userid = await ctx.redis.get('user_' + username + '_' + cls.hash(password))
        if userid:
            this = cls(ctx)
            this.userid = userid.decode('utf-8')
            this.username = username
            this.invoice_manager = InvoiceManager(
                redis=this._redis,
                lightning=this._lightning,
                bitcoind=this._bitcoind,
                userid=this.userid
            )
            return this
        return Error(error_type='AuthenticationError', message='Invalid Credentials')

    async def create(self):
        """create a new user and save to db"""
        username = token_hex(10)

        password = token_hex(10)

        userid = token_hex(10)

        self.username = username
        self.password = password
        self.userid = userid
        await self._redis.set(f'user_{self.username}_{self.hash(self.password)}', self.userid)

    async def save_metadata(self, metadata):
        """save metadata for user to redis"""
        return await self._redis.set('metadata_for_' + self.userid, json.dumps(metadata))

    async def get_address(self):
        """
        return bitcoin address of user. If the address does not exist
        asynchronously generate a new lightning address
        gRPC Response: NewAddressResponse
        see https://api.lightning.community/#newaddress
        for more info

        also sets the invoice managers address
        """
        if not (address := await self._redis.get('bitcoin_address_for_' + self.userid)):
            request = ln.NewAddressRequest(type=0)
            response = await make_async(self._lightning.NewAddress.future(request, timeout=5000))
            self.logger.critical(response)
            address = response.address
            await self._redis.set('bitcoin_address_for_' + self.userid, address)
            self.logger.info(f"Created address: {address} for user: {self.userid}")
            import_response = await self._bitcoind.req(
                'importaddress',
                params={
                    'address': address, 
                    'label': self.userid,
                    'rescan': False
                }
            )
            self.logger.critical(import_response)
            return address
        self.invoice_manager.address = address.decode('utf-8')
        return self.invoice_manager.address


    # async def get_balance(self):
    #     """get the balance for the user"""
    #     balance = await self._redis.get('balance_for_' + self.userid)
    #     if not balance:
    #         balance = await self.get_calculated_balance()
    #         await self.save_balance(balance)
    #     return int(balance)


    # async def save_balance(self, balance):
    #     """save balance to redis"""
    #     key = 'balance_for_' + self.userid
    #     await self._redis.set(key, balance)
    #     await self._redis.expire(key, 1800)

    # async def clear_balance_cache(self):
    #     """clear balance from redis"""
    #     key = 'balance_for_' + self.userid
    #     return self._redis.delete(key)

    async def save_paid_invoice(self, doc):
        """
        saves paid invoice to redis to associate with userid
        invoice can either 
        """
        return await self._redis.rpush('paid_invoices_for' + self.userid, json.dumps(doc))



    # Doesnt belong here FIXME
    async def get_user_by_payment_hash(self, payment_hash):
        """retrives the user by a payment hash in redis"""
        return await self._redis.get('payment_hash_' + payment_hash)

    # async def _list_transactions(self):
    #     response = self.cache['list_transactions']
    #     utc_seconds = (datetime.utcnow() - datetime(1970, 1, 1)).total_seconds()
    #     if response:
    #         if utc_seconds > self.cache['list_transactions_cache_expiry']:
    #             # invalidate cache
    #             self.cache['list_transactions'] = None
    #             self.logger.info('Invalidating context transaction cache')
    #         try:
    #             return json.loads(response)
    #         except json.decoder.JSONDecodeError as error:
    #             self.logger.critical('Could not read json from global transaction cache %s', error)

    #     txs = await self._bitcoind.req('listtransactions', ['*', 100500, 0, True])
    #     self.logger.critical(txs)
    #     ret = {'result': []}
    #     for tx in txs['result']:
    #         ret['result'].append({
    #             'category': tx['category'],
    #             'amount': tx['amount'],
    #             'confirmations': tx['confirmations'],
    #             'address': tx['address'],
    #             'time': tx['time']
    #         })

    #     self.cache['list_transactions'] = json.dumps(ret)
    #     self.cache['list_transactions_cache_expiry'] = utc_seconds + 5 * 60
    #     return ret

    # async def get_pending_txs(self):
    #     """retrives the pending transactions for a user"""
    #     addr = await self.get_address()
    #     if not addr:
    #         raise Exception('cannot get transactions: no onchain address assigned to user')
    #     txs = await self._list_transactions()
    #     txs = txs.result
    #     result = []
    #     for tx in txs:
    #         if tx.confirmations < 3 and tx.address == addr and tx.category == 'receive':
    #             result.append(tx)
    #     return result        
        

    async def account_for_possible_txids(self):
        """performs accounting check for txs"""
        onchain_txs = await self.get_txs()
        imported_txids = await self._redis.lrange('imported_txids_for_' + self.userid, 0, -1)
        for tx in onchain_txs:
            if tx.type != 'bitcoind_tx':
                continue
            already_imported = False
            for imported_txid in imported_txids:
                if tx.txid == imported_txid:
                    already_imported = True

            if not already_imported and tx.category == 'receive':
                lock = Lock(self._redis, 'importing_' + tx.txid)
                if not await lock.obtain_lock():
                    # someones already importing this tx
                    return

                # lock obtained successfully
                user_balance = await self.get_calculated_balance()
                await self.save_balance(user_balance)
                await self._redis.rpush('imported_txids_for_' + self.userid, tx.txid)
                await lock.release_lock()


    async def lock_funds(self, pay_req, decoded_invoice):
        """
        Adds invoice to a list of user's locked payments.
        Used to calculate balance till the lock is lifted
        (payment is in determined state - success or fail)
        """
        utc_seconds = (datetime.utcnow() - datetime.datetime(1970, 1, 1)).total_seconds()
        doc = {
            'pay_req': pay_req,
            'amount': decoded_invoice.num_satoshis,
            'timestamp': utc_seconds
        }
        return self._redis.rpush('locked_payments_for_' + self.userid, json.dumps(doc))


    async def unlock_funds(self, pay_req):
        """
        Strips specific payreq from the list of locked payments
        """
        payments = await self.get_locked_payments()
        save_back = []
        for paym in payments:
            if paym.pay_req != pay_req:
                save_back.append(paym)

        await self._redis.delete('locked_payments_for_' + self.userid)
        for doc in save_back:
            await self._redis.rpush('locked_payments_for_' + self.userid, json.dumps(doc))


    @staticmethod
    def hash(string):
        """returns hex digest of string"""
        hasher = sha256()
        hasher.update(string.encode('utf-8'))
        return hasher.digest().hex()
