from .create_user import MUTATION as _create_user
from .bypass import MUTATION as _bypass
from .login import MUTATION as _login
from .logout import MUTATION as _logout
from .add_invoice import MUTATION as _add_invoice
from .pay_invoice import MUTATION as _pay_invoice
from .bake_macaroon import MUTATION as _bake_macaroon
from .prepay_wallet import MUTATION as _prepay_wallet
from .redeem_wallet import MUTATION as _redeem_wallet

MUTATION = [
    _create_user,
    _bypass,
    _login,
    _logout,
    _add_invoice,
    _pay_invoice,
    _bake_macaroon,
    _prepay_wallet,
    _redeem_wallet
]