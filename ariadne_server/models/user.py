"""module to define user orm of database"""
from context import GINO

db = GINO.db


class User(db.Model):
    """user model"""
    __tablename__ = 'users'

    id = db.Column(db.LargeBinary, primary_key=True, nullable=False)
    username = db.Column(db.LargeBinary, unique=True, nullable=False)
    password_hash = db.Column(db.Text, nullable=False)
    # address can be null if user doesnt request an address
    bitcoin_address = db.Column(db.Text)
    role = db.Column(db.Text, default='user', nullable=False)
    created = db.Column(db.Integer, nullable=False)
