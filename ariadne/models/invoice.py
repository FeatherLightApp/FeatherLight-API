"""Module to define the orm for an invoice"""
import orm
from .base import BaseModel
from .user import User

class Invoice(BaseModel):
    """invoice orm"""
    __tablename__ = 'invoices'

    payment_hash = orm.String(max_length=64, min_length=64, primary_key=True)
    payment_preimage = orm.String(max_length=64, min_length=64)
    payment_request = orm.String(max_length=1024)
    timestamp = orm.Integer(minimum=0)
    expiry = orm.Integer(minimum=0)
    memo = orm.String(max_length=128)
    paid = orm.Boolean(default=False)
    msat_amount = orm.Integer(exclusive_minimum=0)
    # fee null for receivers of invoice
    msat_fee = orm.Integer(minimum=0, allow_null=True) 
    # null if invoice paid to external node
    payee = orm.ForeignKey(User, allow_null=True)
    # null if invoice paid by external node
    payer = orm.ForeignKey(User, allow_null=True)
