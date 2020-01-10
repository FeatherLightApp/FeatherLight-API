from ariadne import UnionType

invoice = UnionType('Invoice')

@invoice.type_resolver
def r_invoice_type(obj, _):
    if obj.hash:
        return 'RemoteInvoice'
    return 'LocalInvoice'
