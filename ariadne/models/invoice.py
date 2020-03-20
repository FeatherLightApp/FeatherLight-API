import orm
from .base import BaseModel

class Invoice(BaseModel):
    __tablename__ = 'invoices'

    payment_hash = orm.String(max_length=100 primary_key=True)