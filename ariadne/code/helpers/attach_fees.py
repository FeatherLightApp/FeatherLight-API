"""Module for adding routing fees to a remote invoice response
DEPRECATED Remove this file in the futuremax 
"""

def attach_fees(invoice):

    if invoice.get('payment_route'):
        invoice['fee'] = int(invoice['payment_route']['total_fees'])
        invoice['value'] = int(invoice['payment_route']['total_fees']) \
            + invoice['payment_route']['total_amt']
        # check if invoice had extra mSats
    if (invoice['payment_route'].get('total_amt_msat') and \
        invoice['payment_route']['total_amt_msat'] / 1000 != int(invoice['payment_route']['total_amt'])
    ):
        # account for mSats
        # value is fees plus max of either value plus one to account for extra sat
        invoice['value'] = invoice['payment_route']['total_fees'] \
            + max(
                int(invoice['payment_route']['total_amt_msat'] / 1000),
                int(invoice['payment_route']['total_amt'])
            ) + 1
    return invoice
    