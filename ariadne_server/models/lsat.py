"""module to define lsat orm of database"""
from typing import Optional
from context import GINO

db = GINO.db


class LSAT(db.Model):
    """user model"""
    __tablename__ = 'lsats'

    # not necessary to store in db but returned to user
    macaroon: Optional[str] = None
    payment_request: Optional[str] = None
    amount: Optional[int] = None

    key = db.Column(db.LargeBinary, unique=True, nullable=False)
    payment_hash = db.Column(db.Text, primary_key=True, nullable=False)
    # hex encoded preimage
    preimage = db.Column(db.Text, unique=True, nullable=False)
    used = db.Column(db.Integer, default=0, nullable=False)
    uses = db.Column(db.Integer, nullable=False)

    