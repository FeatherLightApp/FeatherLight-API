"""Module to define the orm for an invoice"""
from context import GINO

db = GINO.db


class Invoice(db.Model):
    """invoice orm"""
    __tablename__ = 'invoices'

    payment_hash = db.Column(db.LargeBinary, primary_key=True, nullable=False)
    #null before external invoice is paid
    payment_preimage = db.Column(db.LargeBinary)
    payment_request = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.Integer, nullable=False)
    expiry = db.Column(db.Integer, nullable=False),
    # null if paying external invoice with no memo
    memo = db.Column(db.Text)
    paid = db.Column(db.Boolean, nullable=False)
    # null if not yet paid
    paid_at = db.Column(db.Integer)
    msat_amount = db.Column(db.Integer, nullable=False)
    # fee null for receivers of invoice
    msat_fee = db.Column(db.Integer)
    # null if invoice paid to external node
    payee = db.Column(db.Text, db.ForeignKey('users.username'))
    # null if invoice paid by external node
    payer = db.Column(db.Text, db.ForeignKey('users.username'))
