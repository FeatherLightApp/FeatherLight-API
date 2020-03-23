"""Module to define the orm for an invoice"""
import orm
from context import GINO
from .user import User

class Invoice(orm.Model):
    """invoice orm"""
    __tablename__ = 'invoices'

    payment_hash = GINO.db.Column(GINO.db.String(64), primary_key=True, nullable=False)
    payment_preimage = GINO.db.Column(GINO.db.String(64), nullable=False)
    payment_request = GINO.db.Column(GINO.db.String(1024), nullable=False)
    timestamp = GINO.db.Column(GINO.db.Integer, nullable=False)
    expiry = GINO.db.Column(GINO.db.Integer, nullable=False)
    memo = GINO.db.Column(GINO.db.String(128), nullable=False)
    paid = GINO.db.Column(GINO.db.Boolean, nullable=False)
    msat_amount = GINO.db.Column(GINO.db.Integer, nullable=False)
    # fee null for receivers of invoice
    msat_fee = GINO.db.Column(GINO.db.Integer)
    # null if invoice paid to external node
    payee = GINO.db.Column(GINO.db.String(20), GINO.db.ForeignKey('users.id'))
    # null if invoice paid by external node
    payer = GINO.db.Column(GINO.sb.String(20), GINO.db.ForeignKey('users.id'))
