"""module to define user orm of database"""
from context import GINO

db = GINO.db


class User(db.Model):
    """user model"""
    __tablename__ = 'users'

    id = db.Column(db.String(20), primary_key=True, nullable=False)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password_hash = db.Column(db.String(100), nullable=False)
    # address can be null if user doesnt request an address
    bitcoin_address = db.Column(db.String(64))
    role = db.Column(db.String(10), default='user', nullable=False)
