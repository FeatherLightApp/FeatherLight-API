"""Module to define the orm for an invoice"""
from ..context import GINO

db = GINO.db


class Invoice(db.Model):
    """invoice orm"""
    __tablename__ = 'invoices'

    payment_hash = db.Column(db.String(64), primary_key=True, nullable=False)
    payment_preimage = db.Column(db.String(64), nullable=False)
    payment_request = db.Column(db.String(1024), nullable=False)
    timestamp = db.Column(db.Integer, nullable=False)
    expiry = db.Column(db.Integer, nullable=False)
    memo = db.Column(db.String(128), nullable=False)
    paid = db.Column(db.Boolean, nullable=False)
    msat_amount = db.Column(db.Integer, nullable=False)
    # fee null for receivers of invoice
    msat_fee = db.Column(db.Integer)
    # null if invoice paid to external node
    payee = db.Column(db.String(20), db.ForeignKey('users.id'))
    # null if invoice paid by external node
    payer = db.Column(db.String(20), db.ForeignKey('users.id'))
