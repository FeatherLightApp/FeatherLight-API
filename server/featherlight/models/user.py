"""module to define user orm of database"""
from typing import Optional
from context import GINO

db = GINO.db


class User(db.Model):
    """user model"""

    __tablename__ = "users"

    password: Optional[str] = None
    # key for baking macaroons, simply rotate key to revoke all
    key = db.Column(db.LargeBinary, unique=True, nullable=False)
    username = db.Column(db.Text, primary_key=True, nullable=False)
    password_hash = db.Column(db.Text, nullable=False)
    # address can be null if user doesnt request an address
    bitcoin_address = db.Column(db.Text)
    role = db.Column(db.Text, default="user", nullable=False)
    created = db.Column(db.Integer, nullable=False)
