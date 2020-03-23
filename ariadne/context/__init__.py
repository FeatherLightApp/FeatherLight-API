import json
from argon2 import PasswordHasher
from .lightning import LightningStub
from .bitcoin import BitcoinClient
from .redis import RedisConnection
from .database import GINO

ARGON = PasswordHasher()
REDIS = RedisConnection()
LND = LightningStub()
BITCOIND = BitcoinClient()
