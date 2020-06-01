"""Define global singletons that can be accessed throughtout the application"""
from argon2 import PasswordHasher
from .lightning import LightningStub
from .bitcoin import BitcoinClient
from .redis import RedisConnection
from .database import GinoInstance
from .pubsub import PubSubManager

ARGON = PasswordHasher()
REDIS = RedisConnection()
LND = LightningStub()
BITCOIND = BitcoinClient()
GINO = GinoInstance()
PUBSUB = PubSubManager()
