"""module for defining the user class"""
import json
from typing import Union
from math import floor
from secrets import token_hex
from hashlib import sha256
from datetime import datetime
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from code.helpers.async_future import make_async
from code.helpers.mixins import LoggerMixin
from code.classes.lock import Lock
from code.classes.error import Error
import rpc_pb2 as ln


class User(LoggerMixin):
    """defines an instance of a user cache variable is only necessary in
    queries or mutations that call functions requiring the global cache values"""
    def __init__(self, ctx):
        super().__init__()
        self._redis = ctx.redis
        self._bitcoindrpc = ctx.btcd
        self._lightning = ctx.lnd
        self.userid = None
        self.username = None
        self.password = None #only on newly created users. generated pw must be returned to user
        self._access_token = None
        self._refresh_token = None
        self.cache = ctx.cache


    async def get_tokens(self) -> dict:
        #lookup if tokens exist
        if not self._access_token:
            self._access_token = await self._redis.get(f"access_token_for_{self.userid}")
            # convert from bytes to string if access token exists else set value to None
            self._access_token = None if not self._access_token else self._access_token.decode('utf-8')
        if not self._refresh_token:
            self._refresh_token = await self._redis.get(f"refresh_token_for_{self.userid}")
            # convert from bytes to string if refresf token exists else set value to None
            self._refresh_token = None if not self._refresh_token else self._refresh_token.decode('utf-8')
        
        # generate token if they could not be found in redis
        await self._generate_tokens(access = not self._access_token, refresh = not self._refresh_token)
        return {
            'access': self._access_token,
            'refresh': self._refresh_token
        }



    @classmethod
    async def from_jwt(cls, ctx, token: str, kind: str) -> Union[Error, 'User']:
        """Factory method for creating instance from hex token"""
        try:
            jsn = ctx.jwt.decode(token, kind)
            if (userid := await ctx.redis.get(f"userid_for_{jsn.get('token')}")):
                this = cls(ctx)
                this.userid = userid.decode('utf-8')
                return this
            return Error(error_type='AuthenticationError', message='User lookup failed')
        except InvalidTokenError:
            return Error(error_type='AuthenticationError', message='Invalid JSON Web Token')
        except ExpiredSignatureError:
            return Error(error_type='AuthenticationError', message='Token has expired')


    @classmethod
    async def from_credentials(cls, ctx, username: str, password: str) -> Union[Error, 'User']:
        """factory method for instantiating from credentials"""
        userid = await ctx.redis.get('user_' + username + '_' + cls.hash(password))
        if userid:
            this = cls(ctx)
            this.userid = userid.decode('utf-8')
            this.username = username
            # User is loging in with credentials, revoke old tokens and issue new ones
            await this._generate_tokens(refresh=True, access=True)
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
        """
        if not (address := await self._redis.get('bitcoin_address_for_' + self.userid)):
            request = ln.NewAddressRequest(type=0)
            response = await make_async(self._lightning.NewAddress.future(request, timeout=5000))
            adress = response.address
            await self._redis.set('bitcoin_address_for_' + self.userid, address)
            self._bitcoindrpc.req('importaddress', [address, address, False])
            return address
        return address.decode('utf-8')


    async def get_balance(self):
        """get the balance for the user"""
        balance = await self._redis.get('balance_for_' + self.userid)
        if not balance:
            balance = await self.get_calculated_balance()
            await self.save_balance(balance)
        return int(balance)

    async def get_calculated_balance(self):
        """get the calculated balance for the user"""
        calculated_balance = 0

        userinvoices = await self.get_user_invoices()
        for inv in userinvoices:
            if inv and inv.ispaid:
                calculated_balance += inv.amt

        txs = await self.get_txs()
        for tx in txs:
            if tx.type == 'bitcoind_tx':
                calculated_balance += tx.amount * 100000000
            else:
                calculated_balance -= tx.value

        locked_payments = await self.get_locked_payments()
        for paym in locked_payments:
            # locked payments are processed in scripts/pocess-locked-payments
            calculated_balance -= paym.amount + floor(paym.amount * 0.01) #fee limit

        return calculated_balance

    async def save_balance(self, balance):
        """save balance to redis"""
        key = 'balance_for_' + self.userid
        await self._redis.set(key, balance)
        await self._redis.expire(key, 1800)

    async def clear_balance_cache(self):
        """clear balance from redis"""
        key = 'balance_for_' + self.userid
        return self._redis.delete(key)

    async def save_paid_invoice(self, doc):
        """saves paid invoice to redis"""
        return await self._redis.rpush('txs_for_' + self.userid, json.dumps(doc))

    async def add_invoice(self, memo, amt):
        """add invoice and save invoice to redis"""
        # TODO add suport for more custom invoices
        request = ln.Invoice(
            memo=memo,
            value=amt,
            expiry=3600*24
        )
        response = await make_async(self._lightning.AddInvoice.future(request, timeout=5000))
        decoded = await make_async(
            self._lightning.DecodePayReq.future(
                ln.PayReqString(pay_req=response.payment_request)
            )
        )
        await self._redis.set('payment_hash_' + decoded.paymenthash, self.userid)
        await self._redis.rpush('userinvoices_for_' + self.userid, json.dumps(response))
        return response

    # Doesnt belong here FIXME
    async def get_user_by_payment_hash(self, payment_hash):
        """retrives the user by a payment hash in redis"""
        return await self._redis.get('payment_hash_' + payment_hash)

    # Doesnt belong here FIXME
    async def set_payment_hash_paid(self, payment_hash):
        """sets a payment hash as paid in redis"""
        return await self._redis.set('ispaid_' + payment_hash, 1)


    async def lookup_invoice(self, payment_hash):
        """
        asynchronously lookup invoice by its payment hash
        and return a gRPC Response: Invoice
        see https://api.lightning.community/
        for more info
        """
        # TODO validate type of payment hash. Must be bytes
        request = ln.PaymentHash(
            r_hash=payment_hash,
        )
        return await make_async(self._lightning.LookupInvoice.future(request, timeout=5000))

    # Doesnt belong here FIXME
    async def get_payment_hash_paid(self, payment_hash):
        """checks if payment hash is paid in redis"""
        return await self._redis.get('ispaid_' + payment_hash)

    async def get_user_invoices(self):
        """retrives the invoices for the user from lnd via grpc"""
        ranges = await self._redis.lrange('userinvoices_for_' + self.userid, 0, -1)
        result = []
        for invoice in ranges:
            invoice_dict = json.loads(invoice)
            req = ln.PayReqString(pay_req=invoice_dict['payment_request'])
            decoded = await make_async(self._lightning.DecodePayReq.future(req, timeout=5000))
            invoice_ispaid = False
            if self.cache and decoded.paymenthash in self.cache['invoice_ispaid']:
                invoice_ispaid = True
            else:
                invoice_ispaid = bool(await self.get_payment_hash_paid(decoded.payment_hash))
            if not invoice_ispaid:
                utc_seconds = (datetime.utcnow() - datetime.datetime(1970, 1, 1)).total_seconds()
                if decoded and decoded.timestamp > (utc_seconds - 3600 * 24 * 5):
                    # if invoice is not too old we query lnd to find out if its paid
                    lookup_info = await self.lookup_invoice(decoded.paymenthash)
                    if lookup_info.settled:
                        # invoice is actually already paid
                        await self.set_payment_hash_paid(decoded.paymenthash)
                        await self.clear_balance_cache()
            else:
                self.cache['invoice_ispaid'][decoded.paymenthash] = True

            invoice_dict['amount'] = decoded.amount
            invoice_dict['expires'] = decoded.expires
            # TODO ^^ make sure this is correct
            invoice_dict['timestamp'] = decoded.timestamp
            invoice_dict['type'] = 'user_invoice'
            result.append(invoice_dict)

        return result

    async def get_txs(self):
        """retrives the transcations for a user"""
        addr = await self.get_address()
        if not addr:
            raise Exception('cannot get transactions" no onchain address assigned to user')
        txs = await self._list_transactions()
        txs = txs['result']
        result = []
        for tx in txs:
            if 'confirmations' in tx and 'address' in tx and 'category' in tx \
            and tx['confirmations'] >= 3 and tx['address'] == addr and tx['category'] == 'receive':
                tx.type = 'bitcoind_tx'
                result.append(tx)

        ranges = await self._redis.lrange('txs_for_' + self.userid, 0, -1)
        for invoice in ranges:
            invoice = json.loads(invoice)
            invoice['type'] = 'paid_invoice'

            if invoice['payment_route']:
                invoice['fee'] = abs(invoice['payment_route']['total_fees'])
                invoice['value'] = abs(invoice['payment_route']['total_fees']) \
                    + invoice['payment_route']['total_amt']
            else:
                invoice['fee'] = 0

            if invoice['decoded']:
                invoice['timestamp'] = invoice['decoded']['timestamp']
                invoice['memo'] = invoice['decoded']['description']

            # if invoice['payment_preimage']:
            #     invoice['payment_preimage'] = Buffer.from(invoice.payment_preimage, 'hex').toString('hex')

            del invoice['payment_error']
            del invoice['payment_route']
            del invoice['pay_req']
            del invoice['decoded']
            result.append(invoice)

        return result

    async def _list_transactions(self):
        response = self.cache['list_transactions']
        utc_seconds = (datetime.utcnow() - datetime(1970, 1, 1)).total_seconds()
        if response:
            if utc_seconds > self.cache['list_transactions_cache_expiry']:
                # invalidate cache
                self.cache['list_transactions'] = None
                self.logger.info('Invalidating context transaction cache')
            try:
                return json.loads(response)
            except json.decoder.JSONDecodeError as error:
                self.logger.critical('Could not read json from global transaction cache %s', error)

        txs = await self._bitcoindrpc.req('listtransactions', ['*', 100500, 0, True])
        self.logger.critical(txs)
        ret = {'result': []}
        for tx in txs['result']:
            ret['result'].append({
                'category': tx['category'],
                'amount': tx['amount'],
                'confirmations': tx['confirmations'],
                'address': tx['address'],
                'time': tx['time']
            })

        self.cache['list_transactions'] = json.dumps(ret)
        self.cache['list_transactions_cache_expiry'] = utc_seconds + 5 * 60
        return ret

    async def get_pending_txs(self):
        """retrives the pending transactions for a user"""
        addr = await self.get_address()
        if not addr:
            raise Exception('cannot get transactions: no onchain address assigned to user')
        txs = await self._list_transactions()
        txs = txs.result
        result = []
        for tx in txs:
            if tx.confirmations < 3 and tx.address == addr and tx.category == 'receive':
                result.append(tx)
        return result


    async def _generate_tokens(self, **kwargs):
        #function for revoking old tokens if they exist and creating new ones
        # delete old refresh and expire keys before making new ones
        for (token_type, value) in kwargs.items():
            if value and token_type == 'access' or token_type == 'refresh':
                #revoke old token
                self.logger.info(f"Generating new {token_type} token for user: {self.userid}")
                old_token = await self._redis.get(f'{token_type}_token_for_{self.userid}')
                old_token = '' if not old_token else old_token.decode('utf-8')
                await self._redis.delete(f'userid_for_{old_token}')
                await self._redis.delete(f'{token_type}_token_for_{self.userid}')

                #set new token
                if token_type == 'refresh':
                    self._refresh_token = token_hex(20)
                    await self._redis.set('userid_for_' + self._refresh_token, self.userid, expire=604800)
                    await self._redis.set('refresh_token_for_' + self.userid, self._refresh_token, expire=604800)

                if token_type == 'access':
                    self._access_token = token_hex(20)
                    await self._redis.set('userid_for_' + self._access_token, self.userid, expire=900)
                    await self._redis.set('access_token_for_' + self.userid, self._access_token, expire=900)
        
        

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


    async def get_locked_payments(self):
        """retrives the locked payments for a user"""
        payments = await self._redis.lrange('locked_payments_for_' + self.userid, 0, -1)
        result = []
        for paym in payments:
            try:
                data = json.loads(paym)
                result.append(data)
            except json.decoder.JSONDecodeError as error:
                self.logger.critical(error)
        return result


    @staticmethod
    def hash(string):
        """returns hex digest of string"""
        hasher = sha256()
        hasher.update(string.encode('utf-8'))
        return hasher.digest().hex()
