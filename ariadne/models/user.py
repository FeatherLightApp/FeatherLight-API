"""module to define user orm of database"""
import orm
from context import GINO


class User(GINO.db.Model):
    """user model"""
    __tablename__ = 'users'

    id = GINO.db.Column(GINO.db.String(20), primary_key=True)
    username = GINO.db.Column(GINO.db.String(20), unique=True)
    password = GINO.db.Column(GINO.db.String(100))
    # address can be null if user doesnt request an address
    bitcoin_address = GINO.db.Column(GINO.db.String(64), allow_null=True)
    role = GINO.db.Column(GINO.db.String(10), default='user')
