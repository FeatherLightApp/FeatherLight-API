from math import floor
from secrets import token_bytes
from hashlib import sha256
from datetime import datetime
from helpers.async_future import fwrap
import Lock

import rpc_pb2 as ln
import aioify

_invoice_ispaid_cache = {}
_listtransactions_cache = False
_listtransactions_cache_expiry_ts = 0

class User:

    def __init__(self, redis, bitcoindrpc, lightning):
        self._redis = redis
        self._bitcoindrpc = bitcoindrpc
        self._lightning = lightning
        self._userid = None
        self._login = None
        self._pw = None
        self._balance = 0

    def get_user_id(self):
        return self._userid

    def get_login(self):
        return self._login

    def get_pw(self):
        return self._pw

    def get_access_token(self):
        return self._access_token

    def get_refresh_token(self):
        return self._refresh_token

    async def load_by_auth(self, auth):
        if not auth:
            return False
        access_token = authoriztion.replace('Bearer ', '')
        userid = await self._redis.get('userid_for_' + access_token)

        if userid:
            self._userid = userid
            return True
        else:
            return False

    async def load_by_refresh(self, refresh_token):
        user_id = await self._redis.get('userid_for_' + refresh_token)
        if userid:
            self._userid = user_id
            await self._generate_tokens()
            return True
        else:
            return False

    async def create(self):
        login = token_bytes(10).hex()

        pw = token_bytes(10).hex()

        userid = token_bytes(10).hex()
        
        self._login = login
        self._pw = pw
        self._userid = userid
        await self._save_to_db()

    async def save_metadata(self, metadata):
        return await self._redis.set('metadata_for_' + self._userid, json.dumps(metadata))

    async def load_by_credentials(self, login, pw):
        userid = await self._redis.get('user_' + login + '_' + this._hash(pw))

        if userid:
            this._userid = userid
            this._login = login
            this._pw = pw
            await self._generate_tokens()
            return True
        else:
            return False

    async def get_address(self):
        return await self._redis.get('bitcoin_address_for_' + self._userid)

    """
    asynchronously generate a new lightning address
    and return a gRPC Response: NewAddressResponse
    see https://api.lightning.community/#newaddress
    for more info
    """
    async def generate_address(self):
        request = ln.NewAddressRequest(type=0)
        return await fwrap(self._lightning.NewAddress.future(request, timeout=5000))

    async def get_balance(self):
        balance = await self._redis.get('balance_for_' + this._userid) * 1
        if not balance:
            balance = await self.get_calculated_balance()
            await this.save_balance(balance)
        return balance

    async def get_calculated_balance(self):
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
        key = 'balance_for_' + self._userid
        await this._redis.set(key, balance)
        await this._redis.expire(key, 1800)

    async def clear_balance_cache(self):
        key = 'balance_for_' + self._userid
        return self._redis.del(key)

    async def save_user_invoice(self, doc):
        decoded = lightningPayReq.from_string(doc.payment_request)
        await this._redis.set('payment_hash_' + decoded.paymenthash, self._userid)
        return await self._redis.rpush('userinvoices_for_' + self._userid, json.dumps(doc))

    # Doesnt belong here FIXME
    async def get_user_by_payment_hash(self, payment_hash):
        return await self._redis.get('payment_hash_' + payment_hash)

    # Doesnt belong here FIXME
    async def set_payment_hash_paid(self, payment_hash):
        return await self._redis.set('ispaid_' + payment_hash, 1)

    """
    asynchronously lookup invoice by its payment hash
    and return a gRPC Response: Invoice
    see https://api.lightning.community/
    for more info
    """
    async def lookup_invoice(self, payment_hash):
        # TODO validate type of payment hash. Must be bytes
        request = ln.PaymentHash(
            r_hash=payment_hash,
        )
        return await fwrap(self._lightning.LookupInvoice.future(request, timeout=5000))

    # Doesnt belong here FIXME
    async def get_payment_hash_paid(self, payment_hash):
        return await self._redies.get('ispaid_' + payment_hash)

    async def get_user_invoices(self):
        ranges = await self._redis.lrange('userinvoices_for_' + self._userid, 0, -1)
        result = []
        for invoice in ranges:
            invoice_dict = json.loads(invoice)
            decoded = lightningPayReq.from_string(invoice_dict.payment_request)
            invoice_ispaid = _invoice_ispaid_cache[decoded.paymenthash] or \
                bool(await self.get_payment_hash_paid(decoded.paymenthash))
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
                _invoice_ispaid_cache[decoded.paymenthash] = True
            
            invoice_dict['amount'] = decoded.amount
            invoice_dict['expires'] = decoded.expires
            # TODO ^^ make sure this is correct
            invoice_dict['timestamp'] = decoded.timestamp
            invoice_dict['type'] = 'user_invoice'
            result.append(invoice_dict)
        
        return result

            


    async def add_address(self, address):
        await self._redis.set('bitcoin_address_for_' + self._userid, address)

    async def get_txs(self):
        addr = await self.get_address()
        if not addr:
            await self.generate_address()
            addr = await self.get_address()
        if not addr:
            raise Exception('cannot get transactions" no onchain address assigned to user')
        txs = await self._list_transactions()
        txs = txs.result
        result = []
        for tx in txs:
            if tx.confirmations >= 3 and tx.address == addr and tx.category == 'receive':
                tx.type = 'bitcoind_tx'
                result.append(tx)
            
        ranges = await self._redis.lrange('txs_for_' + self._userid, 0, -1)
        for invoice in ranges:
            invoice = JSON.loads(invoice)
            invoice['type'] = 'paid_invoice'

            if invoice['payment_route']:
                invoice['fee'] = abs(invoice['payment_route']['total_fees'])
                invoice['value'] = abs(invoice['payment_route']['total_fees']) + invoice['payment_route']['total_amt']
            else:
                invoice['fee'] = 0

            if invoice['decoded']:
                invoice['timestamp'] = invoice['decoded']['timestamp']
                invoice['memo'] = invoice['decoded']['description']

            if invoice['payment_preimage']:
                # invoice.payment_preimage = Buffer.from(invoice.payment_preimage, 'hex').toString('hex')

            del invoice['payment_error']
            del invoice['payment_route']
            del invoice['pay_req']
            del invoice['decoded']
            result.append(invoice)

        return result

    async def _list_transactions(self):
        response = _listtransactions_cache
        utc_seconds = (datetime.utcnow() - datetime.datetime(1970, 1, 1)).total_seconds()
        if response:
            if (utc_seconds > _listtransactions_cache_expiry_ts):
                # invalidate cache
                response = False
                _listtransactions_cache = False
            try:
                return json.loads(response)
            except json.decoder.JSONDecodeError as e:
                logging.critical(e)
        
        txs = await self._bitcoindrpc.request('listtransacions', ['*', 100500, 0, True])
        ret = { 'result': [] }
        for tx in txs.result:
            ret.result.append({
                'category': tx.category,
                'amount': tx.amount,
                confirmations: tx.confirmations,
                'address': tx.address,
                'time': tx.time
            })

        _listtransactions_cache = json.dumps(ret)
        _listtransactions_cache_expiry_ts = utc_seconds + 5 * 60
        return ret

    async def getPendingTxs(self):
        addr = await self.get_address()
        if not addr:
            await self.generate_address()
            addr = await self.get_address()
        if not addr:
            raise RuntimeError('cannot get transactions: no onchain address assigned to user')
        txs = await self._list_transactions()
        txs = txs.result
        result = []
        for tx in txs:
            if tx.confirmations < 3 and tx.address == addr and tx.category == 'receive':
                result.append(tx)
        return result


    async def _generate_tokens(self):
        buffer = token_bytes(20)
        self._access_token = buffer.hex()

        buffer = token_bytes(20)
        self._refresh_token = buffer.hex()

        await self._redis.set('userid_for_' + self._access_token, self._userid)
        await self._redis.set('userid_for_' + self._refresh_token, self._userid)
        await self._redis.set('access_token_for_' + self._userid, self._access_token)
        await self._redis.set('refresh_token_for_' _ self._userid, self._refresh_token)

    async def _save_to_db(self):
        await self._redis.set('user_{}_{}'.format(self._login, self._hash(self._pw)), self._userid)

    async def account_for_possible_txids(self):
        onchain_txs = await self.get_txs()
        imported_txids = await self._redis.lrange('imported_txids_for_' + self._userid, 0, -1)
        for tx in onchain_txs:
            if tx.type != 'bitcoind_tx': continue
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
                await self._redis.rpush('imported_txids_for_' + self._userid, tx.txid)
                await lock.release_lock()

    """
    Adds invoice to a list of user's locked payments.
    Used to calculate balance till the lock is lifted
    (payment is in determined state - success or fail)
    """
    async def lock_funds(self, pay_req, decoded_invoice):
        utc_seconds = (datetime.utcnow() - datetime.datetime(1970, 1, 1)).total_seconds()
        doc = {
            'pay_req': pay_req,
            'amount': decoded_invoice.num_satoshis,
            'timestamp': utc_seconds
        }
        return self._redis.rpush('locked_payments_for_' + self._userid, json.dumps(doc))

    """
    Strips specific payreq from the list of locked payments
    """
    async def unlock_funds(self, pay_req):
        payments = await self.get_locked_payments()
        save_back = []
        for paym in payments:
            if paym.pay_req != pay_req:
                save_back.append(paym)

        await self._redis.del('locked_payments_for_' + self._userid)
        for doc in save_back:
            await self._redis.rpush('locked_payments_for_' + self._userid, json.dumps(doc))

        
    async def get_locked_payments(self):
        payments = await self._redis.lrange('locked_payments_for_' + self._userid, 0, -1)
        result = []
        for paym in payments:
            try:
                d = json.loads(paym)
                result.append(d)
            except json.decoder.JSONDecodeError as e:
                logging.critical(e)

        return result

    def _hash(self, string):
        h = sha256()
        h.update(string.encode('utf-8'))
        return h.digest().hex()
