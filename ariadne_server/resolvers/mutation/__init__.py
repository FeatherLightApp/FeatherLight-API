from .create_user import MUTATION as create_user
from .bypass import MUTATION as bypass
from .login import MUTATION as login
from .logout import MUTATION as logout
from .add_invoice import MUTATION as add_invoice
from .pay_invoice import MUTATION as pay_invoice
from .bake_macaroon import MUTATION as bake_macaroon
from .prepay_wallet import MUTATION as prepay_wallet
from .redeem_wallet import MUTATION as redeem_wallet

MUTATION = [
    create_user,
    bypass,
    login,
    logout,
    add_invoice,
    pay_invoice,
    bake_macaroon,
    prepay_wallet,
    redeem_wallet
]