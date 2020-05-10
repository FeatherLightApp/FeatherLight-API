from .create_user import MUTATION as create_user
from .bypass import MUTATION as bypass
from .login import MUTATION as login
from .logout import MUTATION as logout
from .add_invoice import MUTATION as add_invoice
from .pay_invoice import MUTATION as pay_invoice
from .bake_macaroon import MUTATION as bake_macaroon

MUTATION = [
    create_user,
    bypass,
    login,
    logout,
    add_invoice,
    pay_invoice,
    bake_macaroon
]