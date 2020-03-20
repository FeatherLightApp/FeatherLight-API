import orm
from .base import BaseModel


class User(BaseModel):
    __tablename__ = 'users'

    id = orm.String(max_length=20, primary_key=True)
    username = orm.String(max_length=20)
    password = orm.String(max_length=100)
    # address can be null if user doesnt request an address
    bitcoin_address = orm.String(max_length=64, allow_null=True)
    role = orm.String(max_length=10, default='user')
