"""module to define user orm of database"""
import orm
from context import DB


class User(orm.Model):
    """user model"""
    __database__ = DB.db
    __metadata__ = DB.metadata
    __tablename__ = 'users'

    id = orm.String(max_length=20, primary_key=True)
    username = orm.String(max_length=20, unique=True)
    password = orm.String(max_length=100)
    # address can be null if user doesnt request an address
    bitcoin_address = orm.String(max_length=64, allow_null=True)
    role = orm.String(max_length=10, default='user')
